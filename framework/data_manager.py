import pandas as pd
from datetime import datetime, timedelta
import talib
import os

class DataManager():
  def __init__(self, data_source, start_dt, end_dt):
    self.start_dt = start_dt
    self.end_dt = end_dt
    self.cur_tick_idx = 0

  def load_bars(self, symbol, timeframe, start_dt, end_dt):
    filename = 'ES_2025.03.28'
    if os.path.exists(f'./data/parquet/{filename}.parquet'):
      min = pd.read_parquet(f'./data/parquet/{filename}.parquet')
    else:
      min = pd.read_csv(f'./data/{filename}.csv')
      min['Datetime'] = pd.to_datetime(min['Date'] + ' ' + min['Time'])
      min['Volume'] = min['Up'] + min['Down']
      min.drop(columns=['Date', 'Time', 'Up', 'Down'], inplace=True)
      min.set_index('Datetime', inplace=True)
      #min.sort_index(ascending=False, inplace=True)
      min.to_parquet(f'./data/parquet/{filename}.parquet')
    print('Data loaded.')
    self.bars = min.loc[start_dt:end_dt].copy()
  
  def get_bars(self, start_dt, end_dt):
    try:
      candles = self.candles.loc[start_dt:end_dt]
    except:
      candles = pd.DataFrame()
    return candles

  def get_indicators(self, candles, indicators):
    for indicator in vars(indicators).values():
      if indicator.val_type == 'latest':
        indicator.value = {
          'SMA': talib.stream.SMA(candles.close, timeperiod=indicator.period)
        }[indicator.name]
    return indicators

  def get_next_tick(self):
    if self.cur_tick_idx >= len(self.tick_df.index):
      return None
    tick = self.tick_df.iloc[self.cur_tick_idx]
    self.cur_tick_idx += 1
    return {
        'symbol': tick.name[0],
        'dt': tick.name[1].to_pydatetime(),
        'ask': tick.Ask,
        'ask_size': tick.Ask_size,
        'bid': tick.Bid,
        'bid_size': tick.Bid_size
      }

  def run(self):
    candles = []
    tick = self.get_next_tick()
    while tick:
      for sub in self.subscriptions:
        if tick['symbol'] == sub['symbol']:
          symbol = tick['symbol']
          if sub['timeframe'] == 'tick':
            sub['callback'](tick)
          else:
            timeframe = sub['timeframe']
            cdle_start, cdle_end = self.get_candle_start_end(tick['dt'], timeframe)
            if symbol not in candles:
              candles[symbol] = {}
            if timeframe not in candles[symbol]:
              candles[symbol][timeframe] = []
            if not len(candles[symbol][timeframe]):
              candles[symbol][timeframe].append({
                'symbol': symbol,
                'start': cdle_start,
                'end': cdle_end,
                'open': tick['bid'],
                'low': tick['bid'],
                'high': tick['bid'],
                'close': tick['bid'],
                'spreads': [tick['ask']-tick['bid']]
              })
            # Check if have to start a new candle or not
            elif candles[symbol][timeframe][-1]['start'] == cdle_start:
              last_cdle = candles[symbol][timeframe][-1]
              last_cdle['low'] = tick['bid'] if tick['bid'] < last_cdle['low'] else last_cdle['low']
              last_cdle['high'] = tick['bid'] if tick['bid'] > last_cdle['high'] else last_cdle['high']
              last_cdle['close'] = tick['bid']
              last_cdle['spreads'] = last_cdle['spreads'] + [tick['ask'] - tick['bid']]
            else: # first tick of new candle
              # Call on_candle callbacks if necessary with all candles up to num_candles
              start_cdle_idx = (len(candles[symbol][timeframe]) - sub['num_candles']) if (len(candles[symbol][timeframe]) - sub['num_candles']) >= 0 else 0
              candles[symbol][timeframe] = candles[symbol][timeframe][start_cdle_idx:]
              sub['callback'](candles[symbol][timeframe])
              # Start new candle
              candles[symbol][timeframe].append({
                'symbol': symbol,
                'start': cdle_start,
                'end': cdle_end,
                'open': tick['bid'],
                'low': tick['bid'],
                'high': tick['bid'],
                'close': tick['bid'],
                'spreads': [tick['ask']-tick['bid']]
              })

  def get_candle_start_end(self, dt, timeframe):
    if timeframe == '1m':
      candle_start = dt.replace(microsecond=0, second=0)
      candle_end = candle_start + timedelta(minutes=1)
    elif timeframe == '5m':
      candle_start = dt - timedelta(minutes=dt.minute % 5, seconds=dt.second, microseconds=dt.microsecond)
      candle_end = candle_start + timedelta(minutes=5)
    elif timeframe == '15m':
      candle_start = dt - timedelta(minutes=dt.minute % 15, seconds=dt.second, microseconds=dt.microsecond)
      candle_end = candle_start + timedelta(minutes=15)
    elif timeframe == '1h':
      candle_start = dt.replace(microsecond=0, second=0, minute=0)
      candle_end = candle_start + timedelta(hours=1)
    elif timeframe == '4h':
      candle_start = dt - timedelta(hours=dt.hour % 4, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
      candle_end = candle_start + timedelta(hours=4)
    return (candle_start, candle_end)

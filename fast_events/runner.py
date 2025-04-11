import numpy as np
from fast_events.framework import load_data, minute_to_timeframe, get_trades_from_signal
from tqdm import tqdm

class Runner:
  def prepare_data(self, data_config):
    print('Loading data...')
    df_min = load_data(data_config.filename)
    print('Resampling data...')
    self.data1 = minute_to_timeframe(df_min, data_config.data1)
    if hasattr(data_config, 'data2'):
        self.data2 = minute_to_timeframe(df_min, data_config.data2)
    else:
        self.data2 = None

  def run(self, strategy_class, strategy_params):
    #print('Pre-calculating indicators...')
    strategy = strategy_class(strategy_params)
    strategy.pre_calc(self.data1, self.data2)

    positions = np.zeros(len(self.data1['datetime']))
    for i in tqdm(range(len(self.data1['datetime'])), desc='Running backtest', unit='bars', colour='green', disable=True):
      if i >= strategy_params.min_bars:
        d1 = {
            'datetime': self.data1['datetime'][:i+1],
            'open': self.data1['open'][:i+1],
            'high': self.data1['high'][:i+1],
            'low': self.data1['low'][:i+1],
            'close': self.data1['close'][:i+1],
            'volume': self.data1['volume'][:i+1]
        }
        d2 = {
            'datetime': self.data2['datetime'][:i+1],
            'open': self.data2['open'][:i+1],
            'high': self.data2['high'][:i+1],
            'low': self.data2['low'][:i+1],
            'close': self.data2['close'][:i+1],
            'volume': self.data2['volume'][:i+1]
        }
        current_position = positions[i-1] 
        positions[i]  = strategy.on_bar(i, d1, d2, current_position)

    df_trades = get_trades_from_signal(self.data1['datetime'], self.data1['open'], self.data1['close'], positions)
    #df_trades['Net Profit'] = df_trades['profit'].cumsum()
    #df_trades['Return %'] = df_trades['profit'] / df_trades['entry_price']
    #df_trades['Cumulative Return %'] = df_trades['Net Profit'] / df_trades['entry_price']
    
    #print('Num trades:', len(df_trades))
    #print('Net profit:', df_trades['profit'].sum())
    if df_trades.empty:
        return 0
    return df_trades['profit'].sum()

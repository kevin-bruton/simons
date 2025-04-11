import numpy as np
import pandas as pd
import os
from enum import Enum

class Timeframe(Enum):
    M1 = '1min'
    M5 = '5min'
    M15 = '15min'
    M30 = '30min'
    H1 = '60min'
    H4 = '4H'
    D1 = 'D'
    W1 = 'W'

def load_data(filename):
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
  return min

def minute_to_timeframe(df_1min: pd.DataFrame, timeframe: Timeframe):
  df_tf = df_1min.resample(timeframe.value).agg({
    "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
  }).dropna()
  return {
      'datetime': df_tf.index.to_numpy(),
      'open': df_tf['Open'].to_numpy(),
      'high': df_tf['High'].to_numpy(),
      'low': df_tf['Low'].to_numpy(),
      'close': df_tf['Close'].to_numpy(),
      'volume': df_tf['Volume'].to_numpy(),
  }

def get_trades_from_signal(time: np.array, open: np.array, close: np.array, signal: np.array) -> pd.DataFrame:
		"""
		Get trades from signal array.
		:param time: Time array.
		:param open: Open array.
		:param close: Close array.
		:param signal: Signal array.
		:return: DataFrame with trades.
		"""
		trades = []
		for i in range(len(signal)):
				if i > 0 and signal[i-1] == 0 and signal[i] == 1:
						trade = {
								'entry_time': time[i],
								'entry_price': open[i],
						}
						trades.append(trade)
				elif i > 0 and signal[i-1] == 1 and signal[i] == 0:
						trades[-1]['exit_time'] = time[i]
						trades[-1]['exit_price'] = close[i]
						trades[-1]['profit'] = close[i] - trades[-1]['entry_price']
		return pd.DataFrame(trades)

class Strategy:
    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("This method should be overridden by subclasses")
#%%
import random
import joblib
import numpy as np
from talib.abstract import ATR
from tqdm import tqdm
#from pyarrow import csv, parquet
import os
import pandas as pd
import matplotlib.pyplot as plt
from fast_events.framework import load_data, minute_to_timeframe, Timeframe, get_trades_from_signal
from joblib import Parallel, delayed
from plot.plot import plot_candlestick_with_trades, plotly_chart
from fast_events.test_strategy import KevStrategy


class KevStrategy:
	def __init__(self, poi_num, atr_mult_num, max_bars_in_trade):
		self.atr_mult = 2.5
		self.max_bars_in_trade = 3
		self.bars_since_entry = 0

	def on_bar(self, time, open, high, low, close, volume, signals, daily_close, atr):
		poi = daily_close[-5]
		entry_level = poi + self.atr_mult * atr[-1]
		if signals[-2] == 0 and high[-1] > entry_level:
			signal = 1
			self.bars_since_entry = 0
		elif signals[-2] == 0:
			signal = 0
		elif signals[-2] == 1 and self.bars_since_entry >= self.max_bars_in_trade:
			signal = 0
		elif signals[-2] == 1:
			signal = 1
			self.bars_since_entry += 1
		return (signal, entry_level)

#%%
print('Loading data...')
filename = 'ES_2025.03.28'
min = load_data(filename)
print('Resampling data...')
tf = minute_to_timeframe(min, Timeframe.H1)
daily = minute_to_timeframe(min, Timeframe.D1)

#%%
"""
max_bars_in_trade = 3
period = 20
atr_mult = 2.5
#poi = tf['Close'].rolling(3).max()
print('POI:', poi)
poi = daily['Close'].shift(5)
"""
time = tf['datetime']
open = tf['open']
high = tf['high']
low = tf['low']
close = tf['close']
volume = tf['volume']
atr = ATR(tf['high'], tf['low'], tf['close'], 20)
#entry_level = poi.to_numpy() #+ atr_mult * atr


min_bars = 21
signals = np.zeros(len(time))
entry_level = np.zeros(len(time))
strat = KevStrategy(poi_num=1, atr_mult_num=2.5, max_bars_in_trade=3)
for i in tqdm(range(len(tf)), desc='Creating signals', unit='bars', colour='green', disable=False):
	if i >= min_bars:
		signals[i], entry_level[i]  = strat.on_bar(time[:i+1], open[:i+1], high[:i+1], low[:i+1], close[:i+1], volume[:i+1], signals[:i+1], daily['Close'].to_numpy()[:i+1], atr[:i+1])
print('Signals created.')

df_trades = get_trades_from_signal(time, open, close, signals)
df_trades['total_profit'] = df_trades['profit'].cumsum()
print('Num trades:', len(df_trades), 'Total profit:', df_trades['total_profit'].iloc[-1])
print('Average profit:', df_trades['profit'].mean(), 'Std:', df_trades['profit'].std())

df_plot = pd.DataFrame({
	'Datetime': tf.index,
	'Open': tf['Open'],
	'High': tf['High'],
	'Low': tf['Low'],
	'Close': tf['Close'],
	'Entry Level': entry_level,
	'Signals': signals
}).set_index('Datetime')
plotly_chart(df_plot.loc['2024-11-20':'2024-11-23'])

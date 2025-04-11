import numpy as np
from talib.abstract import ATR

class KevStrategy:
  def __init__(self, params):
    atr_mult = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3][params.atr_mult_num]
    self.atr_period = [5, 7, 14, 20][params.atr_period_num]
    self.atr_mult = atr_mult
    self.max_bars_in_trade = params.max_bars_in_trade
    self.bars_since_entry = 0
    self.poi_num = params.poi_num
  
  def pre_calc(self, data1, data2):
    self.atr = ATR(data1['high'], data1['low'], data1['close'], self.atr_period)
    self.entry_level = np.zeros(len(data1['datetime']))

  def on_bar(self, bar_num, hourly, daily, current_position):
    high = hourly['high']
    poi = self.get_poi(self.poi_num, daily['open'], daily['close'], hourly['close'])
    #entry_level = hourly['close'][-3:].max() #
    entry_level = poi + self.atr_mult * self.atr[bar_num]
    if current_position == 0 and high[-1] > entry_level:
      signal = 1
      self.bars_since_entry = 0
    elif current_position == 0:
      signal = 0
    elif current_position == 1 and self.bars_since_entry >= self.max_bars_in_trade:
      signal = 0
    elif current_position == 1:
      signal = 1
      self.bars_since_entry += 1
    
    self.entry_level[bar_num] = entry_level
    return signal
  
  def get_poi(self, poi_num, daily_open, daily_close, hourly_close):
    strat_type = 'tf'
    if poi_num == 0: poi = daily_close[-1]
    elif poi_num == 1: poi = daily_open[-1]
    elif poi_num == 2: poi = daily_close[-2]
    elif poi_num == 3: poi = daily_close[-3]
    elif poi_num == 4: poi = daily_close[-4]
    elif poi_num == 5: poi = daily_close[-5]
    elif poi_num == 6: poi = hourly_close[-3:].max()
    elif poi_num == 7: poi = hourly_close[-5:].max()
    elif poi_num == 8: poi = hourly_close[-10:].max()
    elif poi_num == 9: poi = hourly_close[-15:].max()
    elif poi_num == 10: poi = hourly_close[-20:].max()
    elif poi_num == 11: poi = hourly_close[-3:].min()
    elif poi_num == 12: poi = hourly_close[-5:].min()
    elif poi_num == 13: poi = hourly_close[-10:].min()
    elif poi_num == 14: poi = hourly_close[-15:].min()
    elif poi_num == 15: poi = hourly_close[-20:].min()
    return poi
  
  def get_extra_plots(self):
    return {
      'entry_level': self.entry_level,
      'atr': self.atr
    }
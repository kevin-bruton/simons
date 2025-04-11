from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from framework.sim_trader import Trader
from framework.data_manager import DataManager
from framework.reporting.reporter import Reporter

class Backtester:
  def __init__(self, data_source, strategy, bt_config, bars, indicators):
    self.start_dt = bt_config.start_dt
    self.end_dt = bt_config.end_dt
    self.dm = DataManager(data_source, self.start_dt, self.end_dt)
    self.trader = Trader(bt_config.init_balance)
    self.bars = bars
    self.indicators = indicators
    self.strategy = strategy(self.dm, self.trader, bt_config, bars)
    self.onCandle = self.strategy.on_bar
    self.onEnd = self.strategy.on_end
    self.report = Reporter()

  def run(self):
    self.dm.load_bars(self.bars.symbol, self.bars.timeframe, self.start_dt, self.end_dt)
    step_dt = {
        '1m': timedelta(minutes=1)
      }[self.candleData.timeframe]
    current_dt = self.start_dt + (self.bars.num_warmup_candles * step_dt)
    while current_dt < self.end_dt:
      buffer_dt = current_dt - (self.bars.num_warmup_candles * step_dt)
      candles = self.dm.get_bars(buffer_dt, current_dt)
      if not candles.empty:
        indicators = self.dm.get_indicators(candles, self.indicators)
        self.onCandle(candles, indicators)
        self.trader.update_orders_positions({self.bars.symbol: candles.iloc[-1]})
      current_dt += step_dt
    buffer_dt = self.end_dt - (self.bars.num_warmup_candles * step_dt)
    candles = self.dm.get_bars(buffer_dt, self.end_dt)
    if not candles.empty:
      indicators = self.dm.get_indicators(candles, self.indicators)
    self.onEnd(candles, indicators)


  def end(self):
    #self.dm.close()
    pass

    """ month_of_last_trading_day = start_dt.strftime('%Y-%m')
    year_of_last_trading_day = start_dt.strftime('%Y')
    trading_days = self.db.getTradingDaysBetweenDates(start_dt, end_dt)
    for trading_day in trading_days:
      print('\nTRADING DAY:', trading_day)
      month_of_current_trading_day = trading_day.strftime('%Y-%m')
      year_of_current_trading_day = trading_day.strftime('%Y')
      for strategy in self.strategies:
        self.trackPerformance('month', month_of_current_trading_day, month_of_last_trading_day, strategy)
        self.trackPerformance('year', year_of_current_trading_day, year_of_last_trading_day, strategy)
        print(f"{strategy['class'].__class__.__name__} Account value: {strategy['trader'].getAccountValue():.2f}")
        symbols_trading_day_candle = self.db.getCandleForEachSymbolOnDay(symbols, trading_day)
        strategy['trader'].updateOrdersPositionsWithCandle(symbols_trading_day_candle)
        strategy['class'].onTradingDayOpen(trading_day, symbols, symbols_trading_day_candle)
        strategy['trader'].updateOrdersPositionsWithCandle(symbols_trading_day_candle)
      month_of_last_trading_day = month_of_current_trading_day
      year_of_last_trading_day = year_of_current_trading_day """

  def print_trades(self):
    df = pd.DataFrame(self.strategy.trader.get_trades(), columns=['symbol', 'direction', 'quantity', 'opened_dt', 'closed_dt', 'entry', 'exit', 'orig_sl', 'description', 'profit', 'achieved_r'])
    print(df)

  def print_monthly_performance(self):
    print('\n')
    month_perf = self.strategy['monthly_performance']
    for month in month_perf.keys():
      profit = str(f"{month_perf[month]['profit']:.2f}")
      profit_pct = str(f"{month_perf[month]['profit_pct']:.2f}")
      print(f"PERFORMANCE OF MONTH '{month}': Profit: {profit.rjust(10)} Profit%: {profit_pct.rjust(10)}")

  def printYearlyPerformance(self):
    print('\n')
    year_perf = self.strategy['yearly_performance']
    for year in year_perf.keys():
      profit = str(f"{year_perf[year]['profit']:.2f}")
      profit_pct = str(f"{year_perf[year]['profit_pct']:.2f}")
      print(f"PERFORMANCE OF YEAR '{year}':     Profit: {profit.rjust(10)} Profit%: {profit_pct.rjust(10)}")

  def print_account_values(self):
    strat_name = self.strategy.__class__.__name__
    account_val = self.strategy.trader.get_account_value()
    print(f"\nStrategy \"{strat_name}\". Final account value: {account_val:.2f}\n")


  def track_performance(self, timeframe, current, last, strategy):
    current_acc_val = strategy['trader'].get_account_value()
    if current not in strategy[f'{timeframe}ly_performance']:
      strategy[f'{timeframe}ly_performance'][current] = {'start_acc_val': current_acc_val}
      start_acc_val = current_acc_val
    else:
      start_acc_val = strategy[f'{timeframe}ly_performance'][current]['start_acc_val']
    strategy[f'{timeframe}ly_performance'][current]['end_acc_val'] = current_acc_val
    strategy[f'{timeframe}ly_performance'][current]['profit'] = current_acc_val - start_acc_val
    strategy[f'{timeframe}ly_performance'][current]['profit_pct'] = (current_acc_val - start_acc_val) / start_acc_val * 100
    if last != current:
      start_acc_val = strategy[f'{timeframe}ly_performance'][last]['start_acc_val']
      strategy[f'{timeframe}ly_performance'][last]['end_acc_val'] = current_acc_val
      strategy[f'{timeframe}ly_performance'][last]['profit'] = current_acc_val - start_acc_val
      strategy[f'{timeframe}ly_performance'][last]['profit_pct'] = (current_acc_val - start_acc_val) / start_acc_val * 100
      print(f"\n{timeframe.upper()} {last}. Profit: {current_acc_val - start_acc_val:.2f}. Profit %: {(current_acc_val - start_acc_val) / start_acc_val * 100:.2f}\n")

  def init_strategies(self, strategy_alloc, init_balance, start_dt):
    strategies = []
    for strat in strategy_alloc:
      strat_init_balance = init_balance * strat['portfolio_pct'] / 100
      trader = Trader(strat_init_balance)
      strategy = strat['class'](self.db, trader)
      strategies.append({
        'class': strategy,
        'trader': trader,
        'monthly_performance': {start_dt.strftime('%Y-%m'): {'start_acc_val': strat_init_balance}},
        'yearly_performance': {start_dt.strftime('%Y'): {'start_acc_val': strat_init_balance}}
        })
    return strategies

  def all_strategies(self, fn, *args):
    return_vals = []
    return_val = self.strategy[fn](*args)
    return_vals.append(return_val)
    return return_vals
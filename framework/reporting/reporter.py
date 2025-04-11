from pathlib import Path
import pandas as pd
from framework.reporting.chart import Chart

class Reporter():
  def __init__(self, symbol, init_balance, candles, lines, pts_groups, trades):
    self.symbol = symbol
    self.init_balance = init_balance
    self.candles = candles
    self.lines = lines
    self.pts_groups = pts_groups
    self.trades = trades
    """ self.data = {}
    for symbol in symbols:
      self.data[symbol] = {
        'lines_to_plot': plotter.data[symbol]['lines'],
        'scatter_pts_to_plot': plotter.data[symbol]['scatter_pts'],
        'init_balance': init_balance
      } """
  """ 
  def setTrades(self, symbol:str, trades: list, balance: float, num_trades: int, num_wins: int, total_r: float):
    self.data[symbol]['trades'] = trades
    self.data[symbol]['balance'] = balance
    self.data[symbol]['num_trades'] = num_trades
    self.data[symbol]['num_wins'] = num_wins
    self.data[symbol]['total_r'] = total_r """

  """   def getTrades(self, symbol):
    return self.data[symbol]['trades'] """

  def evaluate_performance(self):
    # calculate final balance, num trades, num wins, num losses, win rate, max drawdown
    pass

  def print_results(self, symbol: str):
    init_balance = self.data[symbol]['init_balance']
    balance = self.data[symbol]['balance']
    num_wins = self.data[symbol]['num_wins']
    num_trades = self.data[symbol]['num_trades']
    total_r = self.data[symbol]['total_r']
    avg_r = (total_r / num_trades if num_trades > 0 else 0) if total_r else None
    profit = balance - init_balance
    profit_pct = profit / init_balance * 100
    win_rate = num_wins / num_trades * 100 if num_trades > 0 else None
    print('\nFinal balance: {:.2f} Profit: {:.2f} Profit%: {:.2f}%'.format(balance, profit, profit_pct))
    if num_trades > 0:
      if total_r:
        print('Num trades: {} Num wins: {} Win rate: {:.2f}% Total R:{:.2f} Avg R:{:.2f}\n'.format(num_trades, num_wins, win_rate, total_r, avg_r))
      else:
        print('Num trades: {} Num wins: {} Win rate: {:.2f}%\n'.format(num_trades, num_wins, win_rate))
    else:
      print('No trades were made')

  def print_trades(self, symbol:str):
    print('\n', symbol, 'TRADES:')
    trades = self.data[symbol]['trades']
    if symbol in trades:
      print(pd.DataFrame(self.data[symbol]['trades'][symbol]).to_string(index=False))
    else:
      print('    No trades for this symbol')

  def export_trades_to_excel(self, symbol: str, filename: str):
    """Writes to the filename given and to the sheet with name that coincides with the symbol"""
    filename = f'{filename}-{symbol}.xlsx'
    if Path(filename).exists():
      with pd.ExcelWriter(filename, mode='a') as writer:
        self.data[symbol]['trades'].to_excel(writer, sheet_name=symbol)
    else:
      with pd.ExcelWriter(filename, mode='w') as writer:
        self.data[symbol]['trades'].to_excel(writer, sheet_name=symbol)
  
  def get_chart(self, symbol: str, market_type: str):
    exclude_weekends = {
      'stocks': True,
      'fx': True,
      'crypto': False
    }[market_type]
    exclude_after_hrs = {
      'stocks': True,
      'fx': False,
      'crypto': False
    }[market_type]
    scatter_pts = self.data[symbol]['scatter_pts_to_plot']
    scatter_pts.append({'name': 'Long-Buy', 'color': 'green', 'symbol': 'arrow-up', 'x': [], 'y': []})
    scatter_pts.append({'name': 'Long-Sell', 'color': 'red', 'symbol': 'arrow-down', 'x': [], 'y': []})
    scatter_pts.append({'name': 'Short-Sell', 'color': 'green', 'symbol': 'arrow-down', 'x': [], 'y': []})
    scatter_pts.append({'name': 'Short-Buy', 'color': 'red', 'symbol': 'arrow-up', 'x': [], 'y': []})
    trades = self.data[symbol]['trades']
    if symbol in trades:
      for trade in trades[symbol]:
        for scatter_gp in scatter_pts:
          if trade['direction'] == 'buy':
            if scatter_gp['name'] == 'Long-Buy':
              scatter_gp['x'].append(trade['time_opened'])
              scatter_gp['y'].append(trade['entry_price'])
            elif scatter_gp['name'] == 'Long-Sell':
              scatter_gp['x'].append(trade['time_closed'])
              scatter_gp['y'].append(trade['exit_price'])
          else:
            if scatter_gp['name'] == 'Short-Sell':
              scatter_gp['x'].append(trade['time_opened'])
              scatter_gp['y'].append(trade['entry_price'])
            elif scatter_gp['name'] == 'Short-Buy':
              scatter_gp['x'].append(trade['time_closed'])
              scatter_gp['y'].append(trade['exit_price'])
    return Chart(
        self.data[symbol]['candles'],
        self.data[symbol]['scatter_pts_to_plot'],
        self.data[symbol]['lines_to_plot'],
        exclude_weekends=exclude_weekends,
        exclude_after_hrs=exclude_after_hrs,
        width=800, height=600, margin=dict(l=50, r=50, b=100, t=100, pad=4)
      )
#%%
import random
import joblib
from talib.abstract import ATR
from tqdm import tqdm
#from pyarrow import csv, parquet
import os
import pandas as pd
import matplotlib.pyplot as plt
from vector.data_manager import load_data, minute_to_timeframe, Timeframe
from joblib import Parallel, delayed

# Functions
def get_rand_entry_level(daily, tf):
  
  def calculate_atr(high:pd.Series, low:pd.Series, close:pd.Series, period:int) -> pd.Series:
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr
  
  poi_num = random.randint(0, 10)
  period_num = random.randint(0, 3)
  atr_mult_num = random.randint(0, 10)

  strat_type = random.choice(['tf', 'mr'])
  pois = [daily['Close'].iloc[-1], daily['Open'].iloc[-1], daily['Close'].iloc[-2], daily['Close'].iloc[-3], daily['Close'].iloc[-4], daily['Close'].iloc[-5]]
  if strat_type == 'tf':
    pois += [tf['Close'].rolling(3).max().iloc[-1], tf['Close'].rolling(5).max().iloc[-1], tf['Close'].rolling(10).max().iloc[-1], tf['Close'].rolling(15).max().iloc[-1], tf['Close'].rolling(20).max().iloc[-1]]
  else:
    pois += [tf['Close'].rolling(3).min().iloc[-1], tf['Close'].rolling(5).min().iloc[-1], tf['Close'].rolling(10).min().iloc[-1], tf['Close'].rolling(15).min().iloc[-1], tf['Close'].rolling(20).min().iloc[-1]]
  poi = pois[poi_num]
  period = [5, 7, 14, 20][period_num]
  atr_mult = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3][atr_mult_num]
  
  #entry_level = poi + atr_mult * ATR(tf['High'], tf['Low'], tf['Close'], period) # calculate_atr(tf['High'], tf['Low'], tf['Close'], period)
  atr_mult = 2.5
  period = 20
  poi = daily['Close'].iloc[-5]
  entry_level = poi + atr_mult * calculate_atr(tf['High'], tf['Low'], tf['Close'], period)
  print('Entry level:', entry_level.iloc[-1], 'POI Num:', poi_num, 'POI:', poi, 'ATR Mult:', atr_mult, 'Period:', period, end='; ')
  return entry_level
  #return tf['Close'].rolling(3).max()

# Create a signal column based on the entry level
def create_signal_column(num_bars_to_exit_after, high, level):
    signal = 0
    bars_since_signal = 0
    signal_column = []

    for i in range(len(level)):
        if i > 0 and high[i-1] > level[i-1]:
            signal = 1
            bars_since_signal = 0
        elif bars_since_signal < num_bars_to_exit_after and signal == 1:
            signal = 1
        else:
            signal = 0

        signal_column.append(signal)
        bars_since_signal += 1

    signal = signal_column
    return signal

def get_trades_from_signal_close(df):
	df["entry_price"] = df["Close"].where((df["Signal"] == 1) & (df["Signal"].shift() == 0))
	df['entry_dt'] = df.index.where((df["Signal"] == 1) & (df["Signal"].shift() == 0))
	df["exit_price"] = df["Close"].where((df["Signal"] == 0) & (df["Signal"].shift() == 1))
	df['exit_dt'] = df.index.where((df["Signal"] == 0) & (df["Signal"].shift() == 1))

	# Forward-fill to track trade lifecycle
	df["trade_id"] = df["entry_price"].notna().cumsum()
	df_trades = df.loc[df["exit_price"].notna(), ["trade_id", "exit_price", "exit_dt"]].merge(
			df.loc[df["entry_price"].notna(), ["trade_id", "entry_price", "entry_dt"]],
			on="trade_id"
	)
	# Calculate performance
	df_trades["PnL"] = df_trades["exit_price"] - df_trades["entry_price"]
	#df_trades["return_pct"] = df_trades["PnL"] / df_trades["entry_price"]
	#df_trades["cumulative_PnL"] = df_trades["PnL"].cumsum()
	return df_trades

#%%
print('Loading data...')
filename = 'ES_2025.03.28'
min = load_data(filename)
print('Resampling data...')
tf = minute_to_timeframe(min, Timeframe.H1)
daily = minute_to_timeframe(min, Timeframe.D1)
#%%

num_simulations = 1
direction = 'long'
strategy_type = 'tf'
net_profits = []
run_in_parallel = True
show_progress = False

#%%
# Simulate multiple entry levels and calculate net profit for each simulation
def run_simulation(daily, tf):
  tf['level'] = get_rand_entry_level(daily, tf)
  level = tf['level'].to_numpy()
  high = tf['High'].to_numpy()
  #num_bars_to_exit_after = random.randint(2, 10)
  num_bars_to_exit_after = 3
  tf['Signal'] = create_signal_column(num_bars_to_exit_after, high, level)
  df_trades = get_trades_from_signal_close(tf)
  print('Exit after:', num_bars_to_exit_after, 'Num trades:', len(df_trades), 'Profit:', df_trades['PnL'].sum())
  if df_trades.empty:
    return 0
  return df_trades['PnL'].sum()
  #net_profits.append(df_trades['cumulative_PnL'].iloc[-1])


if run_in_parallel:
	print('Running simulations in parallel on', joblib.cpu_count(), 'cores...')
	net_profits = Parallel(n_jobs=-1)(delayed(run_simulation)(daily.copy(),tf.copy()) for i in tqdm(range(num_simulations), desc="Simulation number", disable=(not show_progress), colour='CYAN'))
else:
	print('Running simulations secuentially...')
	for i in tqdm(range(num_simulations), disable=(not show_progress), colour='CYAN'):
		net_profits.append(run_simulation(daily.copy(),tf.copy()))



# Calculation the percentage of all strategies that are profitable
profitable_strategies = [p for p in net_profits if p > 0]
profitable_strategies_count = len(profitable_strategies)
total_sims = len(net_profits)
profitable_strategies_percentage = profitable_strategies_count / total_sims * 100
#print(net_profits)
print(f"Percentage of profitable strategies: {profitable_strategies_percentage:.2f}%")
print('Num simulations:', len(net_profits))
#%% 

def print_summary(df_trades):
  # Print performance report
  print("Total Trades:", len(df_trades))
  print("Win Rate:", (df_trades["PnL"] > 0).mean())
  print("Net Profit:", df_trades['cumulative_PnL'].iloc[-1])
  print("Avg Trade PnL:", df_trades["PnL"].mean())
  print("Total Return %:", df_trades["return_pct"].sum() * 100)
  print("Avg Return %:", df_trades["return_pct"].mean() * 100)

def plot_cumulative_pnl(df_trades):
  # Plot cumulative PnL
  df_trades["cumulative_PnL"].plot(title="Cumulative PnL", figsize=(12, 4))
  plt.grid(True)
  plt.tight_layout()
  plt.show()

#print_summary(df_trades)
#plot_cumulative_pnl(df_trades)
# %%
"""
if marketPosition = 0 then begin
	haveWaitedAfterLastTrade = barsWaited >= numWaitBars;
	if haveWaitedAfterLastTrade then
		barsWaited = 0
	else
		barsWaited += 1;
		
	if haveWaitedAfterLastTrade and inTradingWindow and (type = "tf" or type = "mr") then begin
		switch (poiNum) begin
			case 0: poi = closeD(1);
			case 1: poi = openD(0);
			case 2: poi = closeD(2);
			case 3: poi = closeD(3);
			case 4: poi = closeD(4);
			case 5: poi = closeD(5);
		end;
		if type = "tf" then begin
			switch (poiNum) begin
				case 6: poi = highest(close,3);
				case 7: poi = highest(close,5);
				case 8: poi = highest(close,10);
				case 9: poi = highest(close,15);
				case 10: poi = highest(close,20);
			end;
		end;
		if type = "mr" then begin
			switch (poiNum) begin
				case 6: poi = lowest(close,3);
				case 7: poi = lowest(close,5);
				case 8: poi = lowest(close,10);
				case 9: poi = lowest(close,15);
				case 10: poi = lowest(close,20);
			end;
		end;

		switch (atrPeriodNum) begin
			case 0: atrPeriod = 5;
			case 1: atrPeriod = 7;
			case 2: atrPeriod = 14;
			case 3: atrPeriod = 20;
		end;

		switch (atrMultNum) begin
			case 0: atrMult = 0;
			case 1: atrMult = 0.25;
			case 2: atrMult = 0.5;
			case 3: atrMult = 0.75;
			case 4: atrMult = 1;
			case 5: atrMult = 1.25;
			case 6: atrMult = 1.5;
			case 7: atrMult = 1.75;
			case 8: atrMult = 2;
			case 9: atrMult = 2.5;
			case 10: atrMult = 3;
		end;
		
		if direction = "long" and (type = "tr" or type = "mr") then
			level = poi + (atrMult * avgTrueRange(atrPeriod))
		else
			level = poi - (atrMult * avgTrueRange(atrPeriod));
			
		if direction = "long" and type = "tf" then
			buy next bar at level stop
		else if direction = "short" and type = "tf" then
			sellShort next bar at level stop
		else if direction = "long" and type = "mr" then
			buy next bar at level limit
		else if direction = "short" and type = "mr" then
			sellShort next bar at level limit;
	end; // end if type = "tf" or type = "mr"
	
	if haveWaitedAfterLastTrade and inTradingWindow and type = "any" then begin
		if direction = "long" then
			buy next bar at market
		else if direction = "short" then
			sellShort next bar at market;
	end;

end; // end if mp = 0

if marketPosition <> 0 then begin // position open
	if barsHeld >= numHoldBars or not inTradingWindow then begin
		if marketPosition > 0 then
			sell next bar at market
		else
			buyToCover next bar at market;
		barsHeld = 0;
	end else
		barsHeld += 1;
		
	
	if closeOnEnd = "week" and dayOfWeek(date) = 5 and time >= sessionEndTime(0, 1) then begin
		if marketPosition > 0 then
			sell("EndWeek") next bar market
		else
			buyToCover("EndWeek") next bar market;
	end;
end;
"""
# %%

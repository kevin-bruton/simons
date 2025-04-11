#%%
import random
from talib.abstract import ATR
from pyarrow import csv, parquet
import os
import pandas as pd

#%%
print('Loading data...')
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

#%%
# Resample to 60-minute data
tf = min.resample('60min').agg({
  'Open': 'first',
  'High': 'max',
  'Low': 'min',
  'Close': 'last',
  'Volume': 'sum'
}).dropna()

# Resample to daily data
daily = min.resample('D').agg({
  'Open': 'first',
  'High': 'max',
  'Low': 'min',
  'Close': 'last',
  'Volume': 'sum'
}).dropna()

#%%
direction = 'long'

poi_num = random.randint(0, 10)
period_num = random.randint(0, 3)
atr_mult_num = random.randint(0, 10)
numHoldBars = random.randint(0, 15) + 5
numWaitBars = random.randint(0,25)

strat_type = random.choice(['tf', 'mr'])
pois = [daily['Close'].iloc[-2], daily['Open'].iloc[-1], daily['Close'].iloc[-3], daily['Close'].iloc[-4], daily['Close'].iloc[-5], daily['Close'].iloc[-6]]
if strat_type == 'tf':
  pois += [tf['Close'].rolling(3).max(), tf['Close'].rolling(5).max(), tf['Close'].rolling(10).max(), tf['Close'].rolling(15).max(), tf['Close'].rolling(20).max()]
else:
  pois += [tf['Close'].rolling(3).min(), tf['Close'].rolling(5).min(), tf['Close'].rolling(10).min(), tf['Close'].rolling(15).min(), tf['Close'].rolling(20).min()]
poi = pois[poi_num]
period = [5, 7, 14, 20][period_num]
atr_mult = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3][atr_mult_num]
entry_level = poi + atr_mult * ATR(tf['High'], tf['Low'], tf['Close'], period)

#%%
tf['level'] = poi + atr_mult * ATR(tf['High'], tf['Low'], tf['Close'], period)

# Upsample signal to 1-min time, forward-fill to cover each high-timeframe window
df_signals_1min = tf['signal'].reindex(min.index, method='ffill')


#%%
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

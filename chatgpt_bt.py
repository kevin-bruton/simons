#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

#%%
# === Step 1: Simulate 1-min data ===#%%
print('Loading data...')
filename = 'ES_2025.03.28'
if os.path.exists(f'./data/parquet/{filename}.parquet'):
  df_1min = pd.read_parquet(f'./data/parquet/{filename}.parquet')
else:
  df_1min = pd.read_csv(f'./data/{filename}.csv')
  df_1min['Datetime'] = pd.to_datetime(df_1min['Date'] + ' ' + df_1min['Time'])
  df_1min['Volume'] = df_1min['Up'] + df_1min['Down']
  df_1min.drop(columns=['Date', 'Time', 'Up', 'Down'], inplace=True)
  df_1min.set_index('Datetime', inplace=True)
  #min.sort_index(ascending=False, inplace=True)
  df_1min.to_parquet(f'./data/parquet/{filename}.parquet')
print('Data loaded.')

#%%
# === Step 2: Resample to 60-min and calculate ATR ===
def true_range(df):
    return pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs()
    ], axis=1).max(axis=1)

df_60min = df_1min.resample("60min").agg({
    "Open": "first", "High": "max", "Low": "min", "Close": "last"
}).dropna()

df_60min["TR"] = true_range(df_60min)
df_60min["ATR"] = df_60min["TR"].rolling(window=5).mean()

# Example signal: ATR > 0.6 triggers "long" signal
df_60min["signal"] = (df_60min["ATR"] > 0.6).astype(int)

#%%
# === Step 3: Map signal to 1-min ===
df_1min["signal_htf"] = df_60min["signal"].reindex(df_1min.index, method="ffill")

#%%
# === Step 4: Backtest logic ===
# Simple strategy: enter long on signal==1, exit when signal turns 0
df_1min["position"] = df_1min["signal_htf"]
df_1min["entry_price"] = df_1min["Close"].where((df_1min["position"] == 1) & (df_1min["position"].shift() == 0))
df_1min["exit_price"] = df_1min["Close"].where((df_1min["position"] == 0) & (df_1min["position"].shift() == 1))

# Forward-fill to track trade lifecycle
df_1min["trade_id"] = df_1min["entry_price"].notna().cumsum()
df_trades = df_1min.loc[df_1min["exit_price"].notna(), ["trade_id", "exit_price"]].merge(
    df_1min.loc[df_1min["entry_price"].notna(), ["trade_id", "entry_price"]],
    on="trade_id"
)

#%%
# === Step 5: Calculate PnL ===
df_trades["PnL"] = df_trades["exit_price"] - df_trades["entry_price"]
df_trades["return_pct"] = df_trades["PnL"] / df_trades["entry_price"]

#%%
# === Step 6: Summary ===
print("Total Trades:", len(df_trades))
print("Win Rate:", (df_trades["PnL"] > 0).mean())
print("Total Return %:", df_trades["return_pct"].sum() * 100)
print("Avg Return %:", df_trades["return_pct"].mean() * 100)

# Plot cumulative PnL
df_trades["cumulative_PnL"] = df_trades["PnL"].cumsum()
df_trades["cumulative_PnL"].plot(title="Cumulative PnL", figsize=(12, 4))
plt.grid(True)
plt.tight_layout()
plt.show()

# %%

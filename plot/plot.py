import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go

def plot_candlestick_with_trades(df, **kwargs):
    """
    Displays a candlestick chart with the Ichimoku indicator overlay based on the provided DataFrame.
    
    Parameters:
    - df: pandas DataFrame with a DatetimeIndex and columns 'Open', 'High', 'Low', 'Close',
          'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span'
    - **kwargs: additional arguments passed to mplfinance.plot (e.g., volume=True, title='Title')
    """
    # Check if the index is of type DatetimeIndex; if not, convert it
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Check if the DataFrame contains the required columns for the candlestick chart
    required_columns = ['Open', 'High', 'Low', 'Close', 'Signals']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("DataFrame must contain the columns: 'Open', 'High', 'Low', 'Close', 'Signals'")
    
    signal_points = df['Close'].where(df['Signals'] == 1)
    add_plots = [
        mpf.make_addplot(signal_points, color='blue', linestyle='-', label='Trade signal'),
    ]
    
    mpf.plot(df, type='candle', addplot=add_plots, **kwargs)

def plotly_chart(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'])])
    signal_points = df['Close'].where(df['Signals'] == 1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Entry Level'], mode='lines', name='Entry Level', marker_color='black'))
    fig.add_trace(go.Scatter(x=df.index, y=signal_points, mode='lines', name='Signals', marker_color='blue'))
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()
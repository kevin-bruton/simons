from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

class Chart():
  def __init__(self, candleDf, scatters=[], lines=[], vrects=[], chart2=False, exclude_after_hrs=False, exclude_weekends=True, width=800, height=800, margin=dict(l=50, r=50, b=100, t=100, pad=4)):
    """ Prepares a Chart object which can  be displayed or printed to a html file
    Parameters:
      candleDf: a DataFrame of candles with columns: date, open, high, low, close
      scatters: a list of groups of points to be displayed. Each scatter group has these properties: name, symbol, color, x (list of date objects),  y (list)
      lines: a list of lines. Properties of each line: name, color, x (list), y (list), chart_num (optional: to specify if to be added to auxiliar chart at the bottom)
      exclude_after_hrs: optional boolean. Default: False. If True exclude hours in chart outside trading hours - useful for stocks
      exclude_weekends: optional boolean. Default: True. If True excludes weekends for time series - useful for forex and stocks
      width: at the moment not being used. Default: uses all available width
      height: height of the graph
      margin: margins of the graph
    """
    df = candleDf.copy()
    data = [
        go.Candlestick(x=df['date'],
          open=df['open'],
          high=df['high'],
          low=df['low'],
          close=df['close'],
          name='Candlesticks',
          increasing_line_color= 'cyan',
          decreasing_line_color= 'gray',
          xaxis="x1",
          yaxis="y1"
        )
      ]
    for scatter in scatters:
      data.append(go.Scatter(
          name=scatter['name'],
          x=scatter['x'],
          y=scatter['y'],
          mode='markers',
          marker={'symbol': scatter['symbol'],'size': 10, 'color': scatter['color']},
          xaxis="x1",
          yaxis="y1"
        ))
    for line in lines:
      if 'chart_num' not in line:
        line['chart_num'] = 1
      data.append(go.Scatter(
        name=line['name'],
        x=line['x'],
        y=line['y'],
        mode='lines',
        line_color=line['color'],
        fill='toself' if 'fill' in line and line['fill'] == True else 'none',
        xaxis="x1",#f"x{line['chart_num']}",
        yaxis=f"y{line['chart_num']}"
      ))
    """if chart2 is False:
      layout = go.Layout(
        height=height
      )"""
    if chart2:
      layout = go.Layout(
        height=height,
        yaxis=dict(
          domain=[0.3, 1]
        ),
        xaxis2=dict(
          anchor="y2",
        ),
        yaxis2=dict(
          domain=[0, 0.27]
        )
      )
    else:
      layout = go.Layout()
    fig = go.Figure(data=data, layout=layout)
    for vr in vrects:
      fig.add_vrect(
        x0=vr['start_dt'], x1=vr['end_dt'],
        fillcolor=vr['fillcolor'], opacity=0.3,
        layer="below", line_width=0,
      )
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        #xaxis={'rangebreaks': [dict(bounds=[22, 3], pattern="hour")]},
        #autosize=False,
        #width=width,
        height=height,
        margin=margin,
        template="plotly_dark",
        dragmode='pan'
      )
    rangebreaks = []
    if exclude_weekends:
      rangebreaks.append(
        dict(bounds=["sat", "mon"]) #hide weekends
      )
    if exclude_after_hrs:
      rangebreaks.append(
        dict(bounds=[22, 15], pattern="hour") #hide hours outside of 9am-5pm
      )
    fig.update_xaxes(
        #type="category",
        rangebreaks=rangebreaks
      )
    self.data = data
    self.fig = fig
    # returns function that receives file name to write the html to 

  def show(self):
    config = {
        'scrollZoom': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape']
    }
    self.fig.show(config=config)

  def write_to_html(self, filename = 'strategies/chart.html'):
    self.fig.write_html(filename)
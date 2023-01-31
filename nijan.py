from tvDatafeed import TvDatafeed, Interval
import talib as ta
import pandas as pd
# pd.set_option('display.max_rows', 1000)
import numpy as np
import datetime
from datetime import time
import matplotlib as plt
from matplotlib.lines import Line2D
import mplfinance as mpf
from yahoo_fin.stock_info import *
from nsepy import get_history
import yfinance as yf



tv = TvDatafeed()

#Download data from stock market
stock_data = yf.download("AAPL", start="2023-01-01", end="2023-01-17",interval= "15m")

data = tv.get_hist(
    symbol='NIFTY',exchange='NSE',interval=Interval.in_15_minute,n_bars=5000, fut_contract = 1
)


# data.to_dict()
print(data)

# # Select data for a specific time period
# start_date = "2023-01-09"
# end_date = "2023-01-13"
# start_time = "09:30:00"
# end_time = "09:45:00"

# selected_data = data["high"].between_time(start_time, end_time).loc[start_date:end_date]
# print(selected_data)

# high_low_data = pd.DataFrame({'high': data.iloc[:1]['high'], 'low': data.iloc[:1]['low']})
# print(data)
# high_low_data = pd.DataFrame({'High': stock_data.iloc[:1].Open, 'Low': stock_data.iloc[:1].Open})

# # Plot the candle chart
# mpf.plot(stock_data, type='candle', addplot=high_low_data)


# Plot the candle chart
# mpf.plot(data, type='candle', addplot = selected_data)
















# b = (a.to_dict())
# for data in b["high"]:
#     print(data)
# # Moving Average
# a[1] = ta.EMA(a['close'], timeperiod = 20)
# a['EMA10'] = ta.EMA(a['close'], timeperiod = 40)
# print(a)
# print(a.to_json())
# c = a.to_dict()


import pandas as pd
import yfinance as yf
import finplot as fplt
import numpy as np
import datetime 
import talib
from PyQt6.QtWidgets import QApplication, QGridLayout, QMainWindow, QGraphicsView, QComboBox, QLabel
from pyqtgraph.dockarea import DockArea, Dock
from threading import Thread
import math

print(yf)






# Downloading financial Data
# data = yf.Ticker("AAPL")
# # Balance_Sheet = data.balance_sheet
# # Balance_Sheet = pd.DataFrame(Balance_Sheet)
# b = data.cash_flow
# dividend = data.dividends
# dividend.index = pd.MultiIndex.from_arrays([dividend.index.date,
#     dividend.index.time], names=['Date','Time'])
# dividend = pd.DataFrame(dividend)
# dividend["Datetime"] = dividend.index
# dividend["Date"] = dividend["Datetime"].dt.date
# dividend["Time"] = dividend["Datetime"].dt.time
# print(b)

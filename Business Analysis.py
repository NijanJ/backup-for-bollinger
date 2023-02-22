import pandas as pd
import yfinance as yf
import finplot as fplt
import numpy as np
import datetime 
import talib
import math
import requests


url = "https://financialmodelingprep.com/api/v3/cash-flow-statement/AAPL?apikey=e04ed607bd57315875138f579e484641&limit=120"
response =requests.get(url)

# print(response.json())
for obj in response.json():
    print(obj["date"][0])










# # If you need to get the column letter, also import this
# from openpyxl.utils import get_column_letter

# janTrading/AAPL-Balance_Sheet.xlsx")
# print(wb)

# ws = wb["Sheet1"]

# # Add value to a cell
# ws['A70'] = "700"
# # # Add a formula to a cell
# # wb['C7'] = '=SUM(C2:C6)'
# # Append a row. Use a list where each value goes to one cell.
# # # to_append = ['A200','end']
# # #Append
# # wb.append(to_append)
# #Save
# wb.save("../NijanTrading/AAPL-Balance_Sheet.xlsx")


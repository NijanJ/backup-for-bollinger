import pandas as pd
import yfinance as yf
import finplot as fplt
import numpy as np
import datetime 
import talib
import math
import requests
import openpyxl
# # If you need to get the column letter, also import this
from openpyxl.utils import get_column_letter

url = "https://financialmodelingprep.com/api/v3/cash-flow-statement/AAPL?apikey=e04ed607bd57315875138f579e484641&limit=120"
response =requests.get(url)
AAPL_Cashflow = response.json()

#Converting Json file to pandas dataframe
AAPL_Cashflow = pd.DataFrame(AAPL_Cashflow)
# print(AAPL_Cashflow["symbol"])
# AAPL_Cashflow = AAPL_Cashflow.drop(["symbol", "cik"], axis = 1)
print(AAPL_Cashflow)




#Converting pandas dataframe to excel file
AAPL_Cashflow_Excel = AAPL_Cashflow.to_excel("AAPL_Cashflow_Excel.xlsx")
# print(response.json())

# for obj in Cashflow:
#     print(obj["date"][0])
# print(Cashflow[["date", "freeCashFlow"]])
# print(Cashflow)






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


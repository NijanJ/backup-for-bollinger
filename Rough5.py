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



## Trading Data
data = yf.download("MSFT", period = "50d", interval = "5m")
data = pd.DataFrame(data)

## separating date and time if datetime is in column not in index
data["Datetime"] = data.index
data['Date'] = data['Datetime'].dt.date
data['Time'] = data['Datetime'].dt.time
data = data.reset_index(drop=True)

## separating date and time if datetime is index
# data.index = pd.MultiIndex.from_arrays([data.index.date,
#     data.index.time], names=['Date','Time'])

## Top Panel and Bottom Panel
ax, ax1= fplt.create_plot(rows=2)
ax.set_visible(xgrid=False, ygrid=False)

# restore view (X-position and zoom) if we ever run this example again
fplt.autoviewrestore()

# overlay volume on the top plot
volumes = data[['Datetime','Open','Close','Volume']]
fplt.volume_ocv(volumes, ax=ax.overlay())

## RSI Calculation
data["RSI"] = talib.RSI(data["Close"],14).round(2)
fplt.plot(data["RSI"], color='#927', legend="RSI", ax = ax1)



## Bollinger Band formula
def get_sma(prices, rate):
    return prices.rolling(rate).mean()

def get_bollinger_bands(prices, rate=20):
    sma = get_sma(prices, rate)
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return bollinger_up, bollinger_down, sma


## Calculating Bollinger Band
bollinger_up, bollinger_down, sma = get_bollinger_bands(data["Close"])
data["bollinger_up"] = bollinger_up
data["bollinger_down"] = bollinger_down
data["SMA"] = sma


## Plot the chart
fplt.plot(data["Datetime"],data["SMA"])
fplt.plot(data["Datetime"], data["bollinger_up"])
fplt.plot(data["Datetime"],data["bollinger_down"])



## Finding Highs touching upper Bollinger Band (Only for Kick) not absolutely necessary
data['BB_High'] = np.where((data["High"] >= data["bollinger_up"]),
     data["High"], np.nan)
data["BB_High"] = pd.DataFrame(data["BB_High"])


## Finding lows touching Lower Bollinger Band
data['BB_Low'] = np.where((data["Low"] <= data["bollinger_down"]),
     data["Low"], np.nan)
data["BB_Low"] = pd.DataFrame(data["BB_Low"])

## PROCESS to find the Exact High and Low.
##1. Finding Shell Swing Highs with help of Lows touching BB
    #1(a). Every High touching BB just before the Low touching BB is shell_swing High
## 2. The first Low touching BB just before Shell Swing HIgh is Shell Swing Low
##3. Finding Exact Swing High:- Highest value between two shell Swing Lows


## 1. Finding Shell Swing Highs with help of Lows touching BB
    #1(a). Every High touching BB just before the Low touching BB is shell_swing High

## For this we first need to find the index of lows touching BB without NAN
BB_Low = np.array(data["BB_Low"])
BB_Low_Wo_Nan = np.where(np.isfinite(BB_Low) ==True)[0].tolist()

## For this we first need to find the index of lows touching BB without NAN
BB_High = np.array(data["BB_High"])
BB_High_Wo_Nan = np.where(np.isfinite(BB_High) ==True)[0].tolist()


## Finding the High touching BB just before the each low from BB_Low_Wo_Nan
Shell_Swing_High_Index_List = []
for i in range(len(BB_Low_Wo_Nan)):
    Shell_Swing_High_Individual_Index = data["BB_High"][:BB_Low_Wo_Nan[i]].last_valid_index()
    Shell_Swing_High_Index_List.append(Shell_Swing_High_Individual_Index)


##2.The first Low touching BB just before Shell Swing HIgh is Shell Swing Low
Shell_Swing_Low_Index_List = []

for i in range(len(BB_High_Wo_Nan)):
    Shell_Swing_Low_Individual_Index = data["BB_Low"][:BB_High_Wo_Nan[i]].last_valid_index()
    Shell_Swing_Low_Index_List.append(Shell_Swing_Low_Individual_Index)


##3. Finding Exact Swing High:- Highest value between two shell Swing Lows 
Exact_Swing_High_Index_List =[]
Exact_Swing_High_Date_List = []
Exact_Swing_High_List =[]
Exact_Swing_High_Volume_List = []
Exact_Swing_High_RSI_List = []
for i in range(len(Shell_Swing_Low_Index_List)):
    if data["High"][Shell_Swing_Low_Index_List[i-1]:Shell_Swing_Low_Index_List[i]].count() > 2:
        Exact_Swing_High_Index = data["High"][Shell_Swing_Low_Index_List[i-1]:Shell_Swing_Low_Index_List[i]].idxmax()
        Exact_Swing_High_Date = data["Datetime"][Exact_Swing_High_Index]
        Exact_Swing_High = data["High"][Exact_Swing_High_Index]
        Exact_Swing_High_Volume = data["Volume"][Exact_Swing_High_Index]
        Exact_Swing_High_RSI = data["RSI"][Exact_Swing_High_Index]
        Exact_Swing_High_Index_List.append(Exact_Swing_High_Index)
        Exact_Swing_High_Date_List.append(Exact_Swing_High_Date)
        Exact_Swing_High_Volume_List.append(Exact_Swing_High_Volume) 
        Exact_Swing_High_List.append(Exact_Swing_High) 
        Exact_Swing_High_RSI_List.append(Exact_Swing_High_RSI) 

##Sorting and deleting duplicates of all the Swing High related lists 
Exact_Swing_High_Index_List =sorted(list(set(Exact_Swing_High_Index_List)))
Exact_Swing_High_Date_List = sorted(list(set(Exact_Swing_High_Date_List)))
Exact_Swing_High_List =sorted(list(set(Exact_Swing_High_List)))
Exact_Swing_High_Volume_List = sorted(list(set(Exact_Swing_High_Volume_List)))
Exact_Swing_High_RSI_List = sorted(list(set(Exact_Swing_High_RSI_List)))


# print(Exact_Swing_High_Date_List)
Exact_Swing_High_Df = {"Exact_Swing_High_Index_List" : Exact_Swing_High_Index_List,
                        "Exact_Swing_High_List" : Exact_Swing_High_List,
                        "Exact_Swing_High_Date_List" : Exact_Swing_High_Date_List,
                        # "Exact_Swing_High_Volume_List" : Exact_Swing_High_Volume_List,
                        "Exact_Swing_High_RSI_List" : Exact_Swing_High_RSI_List,
                        } 

print(len(Exact_Swing_High_Index_List))
print(len(Exact_Swing_High_Date_List))
print(len(Exact_Swing_High_List))
print(len(Exact_Swing_High_Volume_List))
print(len(Exact_Swing_High_RSI_List))


# Exact_Swing_High_Df = pd.DataFrame(Exact_Swing_High_Df) 

# # Plotting Exact Swing high
# for i in range(len(Exact_Swing_High_Df)):
#     fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]), "Hi", color = "#bb7700")
# fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
# fplt.show()



##4. Finding Exact Swing Low:- Lowest value between two Exact Swing Highs
Exact_Swing_Low_Index_List =[]
Exact_Swing_Low_Date_List = []
Exact_Swing_Low_List =[]
Exact_Swing_Low_Volume_List = []
Exact_Swing_Low_RSI_List = []

for i in range(len(Exact_Swing_High_Index_List)):
    if data["Low"][Exact_Swing_High_Index_List[i-1]:Exact_Swing_High_Index_List[i]].count() > 2 :
        Exact_Swing_Low_Index = data["Low"][Exact_Swing_High_Index_List[i-1]:Exact_Swing_High_Index_List[i]].idxmin()
        Exact_Swing_Low_Date = data["Datetime"][Exact_Swing_Low_Index]
        Exact_Swing_Low = data["Low"][Exact_Swing_Low_Index]
        Exact_Swing_Low_Volume = data["Volume"][Exact_Swing_Low_Index]
        Exact_Swing_Low_RSI = data["RSI"][Exact_Swing_Low_Index]
        Exact_Swing_Low_Index_List.append(Exact_Swing_Low_Index)
        Exact_Swing_Low_Index_List.append(Exact_Swing_Low_Index)
        Exact_Swing_Low_Date_List.append(Exact_Swing_Low_Date)
        Exact_Swing_Low_Volume_List.append(Exact_Swing_Low_Volume) 
        Exact_Swing_Low_List.append(Exact_Swing_Low) 
        Exact_Swing_Low_RSI_List.append(Exact_Swing_Low_RSI) 

##Sorting and deleting duplicates of all the Swing Low related lists 
Exact_Swing_Low_Index_List =sorted(list(set(Exact_Swing_Low_Index_List)))
Exact_Swing_Low_Date_List = sorted(list(set(Exact_Swing_Low_Date_List)))
Exact_Swing_Low_List =sorted(list(set(Exact_Swing_Low_List)))
Exact_Swing_Low_Volume_List = sorted(list(set(Exact_Swing_Low_Volume_List)))
Exact_Swing_Low_RSI_List = sorted(list(set(Exact_Swing_Low_RSI_List)))

# print(Exact_Swing_High_Date_List)
Exact_Swing_Low_Df = {"Exact_Swing_Low_Index_List" : Exact_Swing_Low_Index_List,
                        "Exact_Swing_Low_List" : Exact_Swing_Low_List,
                        "Exact_Swing_Low_Date_List" : Exact_Swing_Low_Date_List,
                        "Exact_Swing_High_Volume_List" : Exact_Swing_Low_Volume_List,
                        "Exact_Swing_Low_RSI_List" : Exact_Swing_Low_RSI_List,
                        } 
# Exact_Swing_Low_Df = pd.DataFrame(Exact_Swing_Low_Df) 
# print(len(Exact_Swing_Low_Index_List))
# print(len(Exact_Swing_Low_Date_List))
# print(len(Exact_Swing_Low_List))
# print(len(Exact_Swing_Low_Volume_List))
# print(len(Exact_Swing_Low_RSI_List))

# print(Exact_Swing_Low_Index_List)
# print(Exact_Swing_High_Index_List)
# print(Exact_Swing_Low_Date_List)
# # Plotting Exact Swing high
# for i in range(len(Exact_Swing_High_Df)):
#     fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]), "Lo", color = "#bb7700")
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
fplt.show()


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
data = yf.download("TSLA", period = "50d", interval = "5m")
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
# fplt.plot(data["RSI"], color='#927', legend="RSI", ax = ax1)


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
# fplt.plot(data["Datetime"], data["bollinger_up"])
# fplt.plot(data["Datetime"],data["bollinger_down"])


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


## Storing all the Swing High Related Datas in one variable
Exact_Swing_High_Variables = [Exact_Swing_High_Index_List, Exact_Swing_High_Date_List, Exact_Swing_High_List, 
                            Exact_Swing_High_Volume_List, Exact_Swing_High_RSI_List ]


# Making dataframe of the LISTS related with Swing Highs of same sizes, A PANDAS DATAFRAME
Exact_Swing_High_Df = {"Exact_Swing_High_Index_List" : Exact_Swing_High_Variables[0],
                        "Exact_Swing_High_Date_List" : Exact_Swing_High_Variables[1],
                        "Exact_Swing_High_List" : Exact_Swing_High_Variables[2],
                        "Exact_Swing_High_Volume_List" : Exact_Swing_High_Variables[3],
                        "Exact_Swing_High_RSI_List" : Exact_Swing_High_Variables[4],
                        } 

Exact_Swing_High_Df = pd.DataFrame(Exact_Swing_High_Df).drop_duplicates()
Exact_Swing_High_Df.sort_values(by="Exact_Swing_High_Date_List", inplace = True)
Exact_Swing_High_Df = Exact_Swing_High_Df.reset_index(drop=True)

# To plot RSI and VOlume at the exact swing high in finplot chart, we must convert the pandas data frame column to string list
Exact_Swing_High_RSI_String_List = Exact_Swing_High_Df["Exact_Swing_High_RSI_List"].tolist()
Exact_Swing_High_RSI_String_List = ["RSI = " + str(i) for i in Exact_Swing_High_RSI_String_List]
Exact_Swing_High_Volume_String_List = Exact_Swing_High_Df["Exact_Swing_High_Volume_List"].tolist()
Exact_Swing_High_Volume_String_List = ["Vol = " + str(i)for i in Exact_Swing_High_Volume_String_List]


#  Plotting Exact Swing high
for i in range(len(Exact_Swing_High_Df)):
    fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]), "Hi", color = "#bb7700")
    # fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]*1.006), Exact_Swing_High_RSI_String_List[i], color = "#bb7700")
    fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]*1.004), Exact_Swing_High_Volume_String_List[i], color = "#bb7700")



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
        Exact_Swing_Low_Date_List.append(Exact_Swing_Low_Date)
        Exact_Swing_Low_Volume_List.append(Exact_Swing_Low_Volume) 
        Exact_Swing_Low_List.append(Exact_Swing_Low) 
        Exact_Swing_Low_RSI_List.append(Exact_Swing_Low_RSI) 


## Storing all the Swing High Related Datas in one variable
Exact_Swing_Low_Variables = [Exact_Swing_Low_Index_List, Exact_Swing_Low_Date_List, Exact_Swing_Low_List, 
                            Exact_Swing_Low_Volume_List, Exact_Swing_Low_RSI_List]



# Making dataframe of the LISTS related with Swing Highs of same sizes, A PANDAS DATAFRAME
Exact_Swing_Low_Df = {
    "Exact_Swing_Low_Index_List" : Exact_Swing_Low_Variables[0],
    "Exact_Swing_Low_Date_List" : Exact_Swing_Low_Variables[1],
    "Exact_Swing_Low_List" : Exact_Swing_Low_Variables[2],
    "Exact_Swing_Low_Volume_List" : Exact_Swing_Low_Variables[3],
    "Exact_Swing_Low_RSI_List" : Exact_Swing_Low_Variables[4],
} 

Exact_Swing_Low_Df = pd.DataFrame(Exact_Swing_Low_Df).drop_duplicates()
Exact_Swing_Low_Df.sort_values(by="Exact_Swing_Low_Date_List", inplace = True)
Exact_Swing_Low_Df = Exact_Swing_Low_Df.reset_index(drop=True)

## Converting RSI and Volume pandas data frame column to String List to plot in finplot chart
Exact_Swing_Low_RSI_String_List = Exact_Swing_Low_Df["Exact_Swing_Low_RSI_List"].tolist()
Exact_Swing_Low_RSI_String_List = ["RSI = " + str(i) for i in Exact_Swing_Low_RSI_String_List]
Exact_Swing_Low_Volume_String_List = Exact_Swing_Low_Df["Exact_Swing_Low_Volume_List"].tolist()
Exact_Swing_Low_Volume_String_List = ["Vol = " + str(i) for i in Exact_Swing_Low_Volume_String_List]


#  Plotting Exact Swing high
for i in range(len(Exact_Swing_Low_Df)):
    fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]), "Lo", color = "#bb7700")
    # fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]*0.996), Exact_Swing_Low_RSI_String_List[i], color = "#bb7700")
    fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]*0.994), Exact_Swing_Low_Volume_String_List[i], color = "#bb7700")


# Plotting ORD VOLUME
# Pocess to Plot Ord Volume:
##1 To plot in finplot, Swing High and Low and their Date is merged in same dataframe. For this wee need to put all the datas in the same list AND,
##2.  NEEDS Swing Low and High Values and Date to be of Same size. So SAME SIZE USER DEFINED function is used
##3. Making Pandas Dataframe from same sized swing highs and lows 


##1 To plot in finplot, Swing High and Low and their Date is merged in same dataframe. For this wee need to put all the datas in the same list AND,
## Storing all the Swing High Related Datas in one variable
Ord_Volume = [ Exact_Swing_High_Date_List, Exact_Swing_High_List, 
                            Exact_Swing_Low_Date_List, Exact_Swing_Low_List]


Minimum_Row = min(len(Exact_Swing_High_Df), len(Exact_Swing_Low_Df))
Maximum_Row = max(len(Exact_Swing_High_Df), len(Exact_Swing_Low_Df))
Difference = Maximum_Row - Minimum_Row
if len(Exact_Swing_High_Df) < len(Exact_Swing_Low_Df):
    Ord_Volume_Exact_Swing_Low_Df = Exact_Swing_Low_Df[Difference:].reset_index(drop=True)
    Ord_Volume_Exact_Swing_High_Df = Exact_Swing_High_Df
else:
     Ord_Volume_Exact_Swing_High_Df = Exact_Swing_High_Df[Difference:].reset_index(drop=True)
     Ord_Volume_Exact_Swing_Low_Df = Exact_Swing_Low_Df

Ord_Volume_Exact_Swing_High_Index_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Index_List"].tolist()
Ord_Volume_Exact_Swing_High_Date = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Date_List"].tolist()
Ord_Volume_Exact_Swing_High_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_List"].tolist()
Ord_Volume_Exact_Swing_Low_Index_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Index_List"].tolist()
Ord_Volume_Exact_Swing_Low_Date_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Date_List"].tolist()
Ord_Volume_Exact_Swing_Low_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_List"].tolist()

Ord_Volume_Df = {"Low_Index" : Ord_Volume_Exact_Swing_Low_Index_List, 
    "Low_Date": Ord_Volume_Exact_Swing_Low_Date_List,
    "Low" : Ord_Volume_Exact_Swing_Low_List,
    "High_Index" : Ord_Volume_Exact_Swing_High_Index_List, 
    "High_Date" : Ord_Volume_Exact_Swing_High_Date,
    "High" : Ord_Volume_Exact_Swing_High_List,
}
Ord_Volume_Df = pd.DataFrame(Ord_Volume_Df)
# Swing_Low_DF2.loc[i, "Exact_Swing_Low2"]
for i in range(len(Ord_Volume_Df)):
    fplt.add_line((Ord_Volume_Df.loc[i, "Low_Date"], Ord_Volume_Df.loc[i,"Low"]),
    (Ord_Volume_Df.loc[i,"High_Date"], Ord_Volume_Df.loc[i,"High"]), color='#927', interactive=False, ax = ax1)

for i in range(len(Ord_Volume_Df)):
    if i < Minimum_Row-1:
        fplt.add_line((Ord_Volume_Df.loc[i, "High_Date"], Ord_Volume_Df.loc[i,"High"]),
        (Ord_Volume_Df.loc[i+1,"Low_Date"], Ord_Volume_Df.loc[i+1,"Low"]), color='#9900ff', style='hfukfkuyg', interactive=False, ax = ax1)




print(Ord_Volume_Df)
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]], ax = ax1)
fplt.show()


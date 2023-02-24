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
from numerize import numerize



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
ax, ax1, ax2= fplt.create_plot(rows=3, maximize=True)
ax.set_visible(xgrid=False, ygrid=False)

# restore view (X-position and zoom) if we ever run this example again
fplt.autoviewrestore()

# overlay volume on the top plot
# volumes = data[['Datetime','Open','Close','Volume']]
# fplt.volume_ocv(volumes, ax=ax.overlay())

## RSI Calculation
data["RSI"] = talib.RSI(data["Close"],14).round(2)
# fplt.plot(data["RSI"], color='#927', legend="RSI", ax = ax1)

## MACD Calculation 
data["MACD"],data["Signal"],data["macd_diff"] = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
# fplt.volume_ocv(data[['Datetime','Open','Close','macd_diff']], ax=ax2, colorfunc=fplt.strength_colorfilter)
fplt.plot(data["MACD"], ax=ax2, legend='MACD')
fplt.plot(data["Signal"], ax=ax2, legend='Signal')

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
Exact_Swing_High_MACD_List = []
Exact_Swing_High_Signal_List = []

for i in range(len(Shell_Swing_Low_Index_List)):
    if data["High"][Shell_Swing_Low_Index_List[i-1]:Shell_Swing_Low_Index_List[i]].count() > 2:
        Exact_Swing_High_Index = data["High"][Shell_Swing_Low_Index_List[i-1]:Shell_Swing_Low_Index_List[i]].idxmax()
        Exact_Swing_High_Date = data["Datetime"][Exact_Swing_High_Index]
        Exact_Swing_High = data["High"][Exact_Swing_High_Index]
        Exact_Swing_High_Volume = data["Volume"][Exact_Swing_High_Index]
        Exact_Swing_High_RSI = data["RSI"][Exact_Swing_High_Index]
        Exact_Swing_High_MACD = data["MACD"][Exact_Swing_High_Index]
        Exact_Swing_High_Signal = data["Signal"][Exact_Swing_High_Index]
        Exact_Swing_High_Index_List.append(Exact_Swing_High_Index)
        Exact_Swing_High_Date_List.append(Exact_Swing_High_Date)
        Exact_Swing_High_Volume_List.append(Exact_Swing_High_Volume) 
        Exact_Swing_High_List.append(Exact_Swing_High) 
        Exact_Swing_High_RSI_List.append(Exact_Swing_High_RSI) 
        Exact_Swing_High_MACD_List.append(Exact_Swing_High_MACD)
        Exact_Swing_High_Signal_List.append(Exact_Swing_High_Signal)


## Storing all the Swing High Related Datas in one variable
Exact_Swing_High_Variables = [Exact_Swing_High_Index_List, Exact_Swing_High_Date_List, Exact_Swing_High_List, 
                            Exact_Swing_High_Volume_List, Exact_Swing_High_RSI_List, Exact_Swing_High_MACD_List,
                            Exact_Swing_High_Signal_List ]


# Making dataframe of the LISTS related with Swing Highs of same sizes, A PANDAS DATAFRAME
Exact_Swing_High_Df = {"Exact_Swing_High_Index_List" : Exact_Swing_High_Variables[0],
                        "Exact_Swing_High_Date_List" : Exact_Swing_High_Variables[1],
                        "Exact_Swing_High_List" : Exact_Swing_High_Variables[2],
                        "Exact_Swing_High_Volume_List" : Exact_Swing_High_Variables[3],
                        "Exact_Swing_High_RSI_List" : Exact_Swing_High_Variables[4],
                        "Exact_Swing_High_MACD_List" : Exact_Swing_High_Variables[5],
                        "Exact_Swing_High_Signal_List" : Exact_Swing_High_Variables[6],
                        } 

Exact_Swing_High_Df = pd.DataFrame(Exact_Swing_High_Df).drop_duplicates()
Exact_Swing_High_Df.sort_values(by="Exact_Swing_High_Date_List", inplace = True)
Exact_Swing_High_Df = Exact_Swing_High_Df.reset_index(drop=True)

# To plot RSI and VOlume at the exact swing high in finplot chart, we must convert the pandas data frame column to string list
Exact_Swing_High_RSI_String_List = Exact_Swing_High_Df["Exact_Swing_High_RSI_List"].tolist()
Exact_Swing_High_RSI_String_List = ["RSI = " + str(i) for i in Exact_Swing_High_RSI_String_List]
Exact_Swing_High_Volume_List = np.array(Exact_Swing_High_Volume_List)
Exact_Swing_High_Volume_List[np.isnan(Exact_Swing_High_Volume_List)]=0
Exact_Swing_High_Volume_List = Exact_Swing_High_Volume_List.tolist()
Exact_Swing_High_Volume_String_List = [numerize.numerize(i) for i in Exact_Swing_High_Volume_List]


#  Plotting Exact Swing high
for i in range(len(Exact_Swing_High_Df)):
    # fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]), "Hi", color = "#bb7700")
    # fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]*1.006), Exact_Swing_High_RSI_String_List[i], color = "#bb7700")
    fplt.add_text((Exact_Swing_High_Df.loc[i, "Exact_Swing_High_Date_List"], Exact_Swing_High_Df.loc[i, "Exact_Swing_High_List"]*1.004),"U " + Exact_Swing_High_Volume_String_List[i], color = "#bb7700")



##4. Finding Exact Swing Low:- Lowest value between two Exact Swing Highs
Exact_Swing_Low_Index_List =[]
Exact_Swing_Low_Date_List = []
Exact_Swing_Low_List =[]
Exact_Swing_Low_Volume_List = []
Exact_Swing_Low_RSI_List = []
Exact_Swing_Low_MACD_List = []
Exact_Swing_Low_Signal_List = []

for i in range(len(Exact_Swing_High_Index_List)):
    if data["Low"][Exact_Swing_High_Index_List[i-1]:Exact_Swing_High_Index_List[i]].count() > 2 :
        Exact_Swing_Low_Index = data["Low"][Exact_Swing_High_Index_List[i-1]:Exact_Swing_High_Index_List[i]].idxmin()
        Exact_Swing_Low_Date = data["Datetime"][Exact_Swing_Low_Index]
        Exact_Swing_Low = data["Low"][Exact_Swing_Low_Index]
        Exact_Swing_Low_Volume = data["Volume"][Exact_Swing_Low_Index]
        Exact_Swing_Low_RSI = data["RSI"][Exact_Swing_Low_Index]
        Exact_Swing_Low_MACD = data["MACD"][Exact_Swing_Low_Index]
        Exact_Swing_Low_Signal = data["Signal"][Exact_Swing_Low_Index]
        Exact_Swing_Low_Index_List.append(Exact_Swing_Low_Index)
        Exact_Swing_Low_Date_List.append(Exact_Swing_Low_Date)
        Exact_Swing_Low_Volume_List.append(Exact_Swing_Low_Volume) 
        Exact_Swing_Low_List.append(Exact_Swing_Low) 
        Exact_Swing_Low_RSI_List.append(Exact_Swing_Low_RSI)
        Exact_Swing_Low_MACD_List.append(Exact_Swing_Low_MACD) 
        Exact_Swing_Low_Signal_List.append(Exact_Swing_Low_Signal) 


## Storing all the Swing High Related Datas in one variable
Exact_Swing_Low_Variables = [Exact_Swing_Low_Index_List, Exact_Swing_Low_Date_List, Exact_Swing_Low_List, 
                            Exact_Swing_Low_Volume_List, Exact_Swing_Low_RSI_List, Exact_Swing_Low_MACD_List,
                            Exact_Swing_Low_Signal_List]



# Making dataframe of the LISTS related with Swing Highs of same sizes, A PANDAS DATAFRAME
Exact_Swing_Low_Df = {
    "Exact_Swing_Low_Index_List" : Exact_Swing_Low_Variables[0],
    "Exact_Swing_Low_Date_List" : Exact_Swing_Low_Variables[1],
    "Exact_Swing_Low_List" : Exact_Swing_Low_Variables[2],
    "Exact_Swing_Low_Volume_List" : Exact_Swing_Low_Variables[3],
    "Exact_Swing_Low_RSI_List" : Exact_Swing_Low_Variables[4],
    "Exact_Swing_Low_MACD_List" : Exact_Swing_Low_Variables[5],
    "Exact_Swing_Low_Signal_List" : Exact_Swing_Low_Variables[6]
} 

Exact_Swing_Low_Df = pd.DataFrame(Exact_Swing_Low_Df).drop_duplicates()
Exact_Swing_Low_Df.sort_values(by="Exact_Swing_Low_Date_List", inplace = True)
Exact_Swing_Low_Df = Exact_Swing_Low_Df.reset_index(drop=True)

## Converting RSI and Volume pandas data frame column to String List to plot in finplot chart
Exact_Swing_Low_RSI_String_List = Exact_Swing_Low_Df["Exact_Swing_Low_RSI_List"].tolist()
Exact_Swing_Low_RSI_String_List = ["RSI = " + str(i) for i in Exact_Swing_Low_RSI_String_List]
Exact_Swing_Low_Volume_List = np.array(Exact_Swing_Low_Volume_List)
Exact_Swing_Low_Volume_List[np.isnan(Exact_Swing_Low_Volume_List)]=0
Exact_Swing_Low_Volume_List = Exact_Swing_Low_Volume_List.tolist()
Exact_Swing_Low_Volume_String_List = [numerize.numerize(i) for i in Exact_Swing_Low_Volume_List]
# Exact_Swing_Low_Volume_String_List = Exact_Swing_Low_Df["Exact_Swing_Low_Volume_List"].tolist()
# Exact_Swing_Low_Volume_String_List = ["Vol = " + str(i) for i in Exact_Swing_Low_Volume_String_List]


#  Plotting Exact Swing high
for i in range(len(Exact_Swing_Low_Df)):
    # fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]), "Lo", color = "#bb7700")
    # fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]*0.996), Exact_Swing_Low_RSI_String_List[i], color = "#bb7700")
    fplt.add_text((Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_Date_List"], Exact_Swing_Low_Df.loc[i, "Exact_Swing_Low_List"]*0.994), "D " + Exact_Swing_Low_Volume_String_List[i], color = "#bb7700")



# PLOTTING ORD VOLUME
# Pocess to Plot Ord Volume:
#1. To plot ord volume in chart, we must create new dataframe comprising Exact Swing High and Exact Swing Low.
    #i. But the problem is Exact Swing High and Exact Swing Low dataframe's number of rows vary. So the number of row of both these dataframe is made same.
    #ii. While making the number of rows same, the dataframe with larger number of rows is sliced from old value as new value cant be sliced(as it is important for analysis)
    #iii. then the sliced dataframe returned is valid for ord volume.

#2. Putting the two dataframes(valid for ord volume) is then put into same dataframe.
    #i.For this, we need to convert the columns required to plot ord volume into the list. then we can create the dataframe.
    #ii. Creating dictionary of lists to convert into dataframe
    #iii. Create Dataframe

##3. Calculating ORD volume(average) volume between swing high and swing low.
    #i.For this we need to check which comes first in Ord volume dataframe, ord swing or ord Swing low.
    #ii. then we can coomput average volume from index of ord swing high and ord Swing low
    #iii.  The average number returned by python with mean() function is in large decimal value which is difficult to read. so NUmerize librarry is used convert them to readable form. ##function convert the values automaically into string.

##4.  The chart become too rough when ord volume is plotted in same main chart. so it is plotted in different pane.
      #i. For this we need to create candlestick chart in another pane again.
      #ii. Plotting Ord volume in secondary candlestick chart.



#1. To plot ord volume in chart, we must create new dataframe comprising Exact Swing High and Exact Swing Low.
    #i. But the problem is Exact Swing High and Exact Swing Low dataframe's number of rows vary. So the number of row of both these dataframe is made same.
    #ii. While making the number of rows same, the dataframe with larger number of rows is sliced from old value as new value cant be sliced(as it is important for analysis)
    #iii. then the sliced dataframe returned is valid for ord volume. 

Minimum_Row = min(len(Exact_Swing_High_Df), len(Exact_Swing_Low_Df))
Maximum_Row = max(len(Exact_Swing_High_Df), len(Exact_Swing_Low_Df))
Difference = Maximum_Row - Minimum_Row


if len(Exact_Swing_High_Df) < len(Exact_Swing_Low_Df):
    Ord_Volume_Exact_Swing_Low_Df = Exact_Swing_Low_Df[Difference:].reset_index(drop=True) ##Sliced old value 
    Ord_Volume_Exact_Swing_High_Df = Exact_Swing_High_Df
else:
     Ord_Volume_Exact_Swing_High_Df = Exact_Swing_High_Df[Difference:].reset_index(drop=True) ##Sliced old value 
     Ord_Volume_Exact_Swing_Low_Df = Exact_Swing_Low_Df



#2. Putting the two dataframes(valid for ord volume) is then put into same dataframe.
    #i.For this, we need to convert the columns required to plot ord volume into the list. then we can create the dataframe.
    #ii. Creating dictionary of lists to convert into dataframe
    ##iii. Create Dataframe

Ord_Volume_Exact_Swing_High_Index_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Index_List"].tolist()
Ord_Volume_Exact_Swing_High_Date = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Date_List"].tolist()
Ord_Volume_Exact_Swing_High_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_List"].tolist()
Ord_Volume_Exact_Swing_High_Volume_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Volume_List"].tolist()
Ord_Volume_Exact_Swing_High_MACD_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_MACD_List"].tolist()
Ord_Volume_Exact_Swing_High_Signal_List = Ord_Volume_Exact_Swing_High_Df["Exact_Swing_High_Signal_List"].tolist()
Ord_Volume_Exact_Swing_Low_Index_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Index_List"].tolist()
Ord_Volume_Exact_Swing_Low_Date_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Date_List"].tolist()
Ord_Volume_Exact_Swing_Low_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_List"].tolist()
Ord_Volume_Exact_Swing_Low_Volume_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Volume_List"].tolist()
Ord_Volume_Exact_Swing_Low_MACD_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_MACD_List"].tolist()
Ord_Volume_Exact_Swing_Low_Signal_List = Ord_Volume_Exact_Swing_Low_Df["Exact_Swing_Low_Signal_List"].tolist()

#ii. Creating dictionary of lists to convert into dataframe
Ord_Volume_Df = {
    "Ord_Swing_Low_Index" : Ord_Volume_Exact_Swing_Low_Index_List, 
    "Ord_Swing_Low_Date": Ord_Volume_Exact_Swing_Low_Date_List,
    "Ord_Swing_Low" : Ord_Volume_Exact_Swing_Low_List,
    "Ord_Swing_Low_Volume" : Ord_Volume_Exact_Swing_Low_Volume_List,
    "Ord_Swing_Low_MACD" : Ord_Volume_Exact_Swing_Low_MACD_List,
    "Ord_Swing_Low_Signal" : Ord_Volume_Exact_Swing_Low_Signal_List,
    "Ord_Swing_High_Index" : Ord_Volume_Exact_Swing_High_Index_List, 
    "Ord_Swing_High_Date" : Ord_Volume_Exact_Swing_High_Date,
    "Ord_Swing_High" : Ord_Volume_Exact_Swing_High_List,
    "Ord_Swing_High_Volume" : Ord_Volume_Exact_Swing_High_Volume_List,
    "Ord_Swing_High_MACD" : Ord_Volume_Exact_Swing_High_MACD_List,
    "Ord_Swing_High_Signal" : Ord_Volume_Exact_Swing_High_Signal_List,
}

##iii. Create Dataframe
Ord_Volume_Df = pd.DataFrame(Ord_Volume_Df)


##3. Calculating ORD volume(average) volume between swing high and swing low.
    #i.For this we need to check which comes first in Ord volume dataframe, ord swing or ord Swing low.
    #ii. then we can coomput average volume from index of ord swing high and ord Swing low
    #iii.  The average number returned by python with mean() function is in large decimal value which is difficult to read. so NUmerize librarry is used convert them to readable form. ##function convert the values automaically into string.
    #iii. plotting ord line from swing low to swing high
    #iv. plotting ord line from swing high to swing low

##Ord volume of UpSwing
Ord_Volume_Upswing_List = []
for i in range(len(Ord_Volume_Exact_Swing_High_Index_List)):
    if i < Minimum_Row-1:
        Ord_Volume = data["Volume"][Ord_Volume_Df["Ord_Swing_Low_Index"][i]:Ord_Volume_Df["Ord_Swing_High_Index"][i+1]].mean()  #ii. then we can coomput average volume from index of ord swing high and ord Swing low
        Ord_Volume_Upswing_List.append(Ord_Volume)

#iii.  The average number returned by python with mean() function is in large decimal value which is difficult to read. so NUmerize librarry is used convert them to readable form. Numerize
        ##function convert the values automaically into string.
Ord_Volume_Upswing_String_List = [numerize.numerize(i) for i in Ord_Volume_Upswing_List]
print(Ord_Volume_Upswing_String_List)

##Ord volume of DownSwing
Ord_Volume_Downswing_List = []
for i in range(len(Ord_Volume_Exact_Swing_Low_Index_List)):
    if i < Minimum_Row-1:
        Ord_Volume = data["Volume"][Ord_Volume_Df["Ord_Swing_High_Index"][i]:Ord_Volume_Df["Ord_Swing_Low_Index"][i+1]].mean()  #ii. then we can coomput average volume from index of ord swing high and ord Swing low
        Ord_Volume_Downswing_List.append(Ord_Volume)
Ord_Volume_Downswing_List = np.array(Ord_Volume_Downswing_List)
Ord_Volume_Downswing_List[np.isnan(Ord_Volume_Downswing_List)]=0
Ord_Volume_Downswing_List = Ord_Volume_Downswing_List.tolist()
#iii.  The average number returned by python with mean() function is in large decimal value which is difficult to read. so NUmerize librarry is used convert them to readable form. Numerize
        ##function convert the values automaically into string.

# Ord_Volume_Downswing_String_List = [numerize.numerize(i) for i in Ord_Volume_Downswing_List]
print(numerize.numerize(Ord_Volume_Downswing_List[0]))
# print(Ord_Volume_Downswing_List)
Ord_Volume_Downswing_String_List = [numerize.numerize(i) for i in Ord_Volume_Downswing_List]
print(Ord_Volume_Downswing_String_List)
# print(data["Volume"][Ord_Volume_Df["Ord_Swing_High_Index"][1]])



##4.  The chart become too rough when ord volume is plotted in same main chart. so it is plotted in different pane.
      #i. For this we need to create candlestick chart in another pane again.
      #ii. Plotting Ord volume in secondary candlestick chart.
      #iii. plotting ord line from swing low to swing high
      #iv. plotting ord line from swing high to swing low

#i. For this we need to create candlestick chart in another pane again.
fplt.candle_bull_color = fplt.candle_bear_color = fplt.candle_bear_body_color = '#e6e6e6'
# fplt.volume_bull_color = fplt.volume_bear_color = '#333'
fplt.candle_bull_body_color = fplt.volume_bull_body_color = '#e6e6e6'
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]], ax = ax1)

 #ii. Plotting Ord volume of upswing in secondary candlestick chart.
for i in range(len(Ord_Volume_Upswing_String_List)):
    fplt.add_text((Ord_Volume_Df.loc[i, "Ord_Swing_High_Date"], Ord_Volume_Df.loc[i, "Ord_Swing_High"]*1.01), "OU " + Ord_Volume_Upswing_String_List[i] , color = "#bb7700", ax = ax)

 #ii. Plotting Ord volume of upswing in secondary candlestick chart.
for i in range(len(Ord_Volume_Downswing_String_List)):
    fplt.add_text((Ord_Volume_Df.loc[i, "Ord_Swing_Low_Date"], Ord_Volume_Df.loc[i, "Ord_Swing_Low"]*0.99), "OD " + Ord_Volume_Downswing_String_List[i] , color = "#bb7700", ax = ax)

#iii. plotting ord line from swing low to swing high
for i in range(len(Ord_Volume_Df)):
    fplt.add_line((Ord_Volume_Df.loc[i, "Ord_Swing_Low_Date"], Ord_Volume_Df.loc[i,"Ord_Swing_Low"]),
    (Ord_Volume_Df.loc[i,"Ord_Swing_High_Date"], Ord_Volume_Df.loc[i,"Ord_Swing_High"]), color='#000', interactive=False, ax = ax1)

#iv. plotting ord line from swing high to swing low
for i in range(len(Ord_Volume_Df)):
    if i < Minimum_Row-1:
        fplt.add_line((Ord_Volume_Df.loc[i, "Ord_Swing_High_Date"], Ord_Volume_Df.loc[i,"Ord_Swing_High"]),
        (Ord_Volume_Df.loc[i+1,"Ord_Swing_Low_Date"], Ord_Volume_Df.loc[i+1,"Ord_Swing_Low"]), color='#000', style='hfukfkuyg', interactive=False, ax = ax1)







## Backtesting
##1. Comparing ord volume of downswing and upswing when high and previous high and low and previous low is at same level
##1(i). Comparing ord volume of downswing and upswing for short-selling
for i in range(len(Ord_Volume_Upswing_List)):
    try:
        if Ord_Volume_Upswing_List[i+1] and Ord_Volume_Downswing_List[i+1] is not None:
            if Ord_Volume_Upswing_List[i+1] < Ord_Volume_Downswing_List[i+1] and Ord_Volume_Df["Ord_Swing_High"][i+1] > Ord_Volume_Df["Ord_Swing_High"][i] :
                fplt.add_text((Ord_Volume_Df.loc[i+1, "Ord_Swing_High_Date"], Ord_Volume_Df.loc[i+1, "Ord_Swing_High"]*1.02), "Short-Sell" , color = "#eb719e", ax=ax1)
    except IndexError as e:
        print(e)

##1(ii). Comparing ord volume of Upswing and Downswing for Buying
for i in range(len(Ord_Volume_Upswing_List)):
    try:
        if Ord_Volume_Upswing_List[i+1] and Ord_Volume_Downswing_List[i+1] is not None:
            if Ord_Volume_Upswing_List[i+1] > Ord_Volume_Downswing_List[i+1] and Ord_Volume_Df["Ord_Swing_Low"][i+1] < Ord_Volume_Df["Ord_Swing_Low"][i] :
                fplt.add_text((Ord_Volume_Df.loc[i+1, "Ord_Swing_Low_Date"], Ord_Volume_Df.loc[i+1, "Ord_Swing_Low"]*1.02), "Buy" , color = "#5abeb0", ax=ax1)
    except IndexError as e:
        print(e)
        


##2. Comparing ord volume of downswing and upswing when price is making higher high and lower low
#2.(i) TOPPING PATTERN(Comparing two upswing volume, to know wether stock still have enough energy(volume) to move above. IF volume is low in current Up-leg than previous
#upleg, stock has become weak and we can sell.
#Bearish MACD Crossover
def Bearish_MACD_Crossover():
    for i in range(len(Ord_Volume_Df)):
        if Ord_Volume_Df["Ord_Swing_Low_MACD"][i] > Ord_Volume_Df["Ord_Swing_Low_Signal"][i] and Ord_Volume_Df["Ord_Swing_Low_MACD"][i+1] < Ord_Volume_Df["Ord_Swing_Low_Signal"][i+1]:
            return Ord_Volume_Df["Ord_Swing_Low_MACD"][i] > Ord_Volume_Df["Ord_Swing_Low_Signal"][i] and Ord_Volume_Df["Ord_Swing_Low_MACD"][i+1] < Ord_Volume_Df["Ord_Swing_Low_Signal"][i+1]

for i in range(len(Ord_Volume_Upswing_List)):
    try:
        if Ord_Volume_Upswing_List[i+1] is not None:
            if Ord_Volume_Upswing_List[i+1] < Ord_Volume_Upswing_List[i] and Ord_Volume_Df["Ord_Swing_High"][i+1] > Ord_Volume_Df["Ord_Swing_High"][i] and Ord_Volume_Df["Ord_Swing_Low"][i+1] > Ord_Volume_Df["Ord_Swing_Low"][i] and Bearish_MACD_Crossover:
                fplt.add_text((Ord_Volume_Df.loc[i+1, "Ord_Swing_High_Date"], Ord_Volume_Df.loc[i+1, "Ord_Swing_High"]*0.998), "Short-Sell in uptrend" , color = "#eb719e", ax=ax1)
    except IndexError as e:
        print(e)




# # change to b/w coloring templates for next plots
fplt.candle_bull_color = fplt.candle_bear_color = fplt.candle_bear_body_color = '#000'
# fplt.volume_bull_color = fplt.volume_bear_color = '#333'
fplt.candle_bull_body_color = fplt.volume_bull_body_color = '#fff'
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
# fplt.show()




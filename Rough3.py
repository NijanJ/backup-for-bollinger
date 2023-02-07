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

app = QApplication([])
win = QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1600,800)
win.setWindowTitle("Docking charts example for finplot")

# Set width/height of QSplitter
win.setStyleSheet("QSplitter { width : 20px; height : 20px; }")

# Create docks
dock_0 = Dock("dock_0", size = (1000, 100), closable = True)
dock_1 = Dock("dock_1", size = (1000, 100), closable = True)
dock_2 = Dock("dock_2", size = (1000, 100), closable = True)
area.addDock(dock_0)
area.addDock(dock_1)
area.addDock(dock_2)


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

## RSI
data["RSI"] = talib.RSI(data["Close"],14)
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



## Finding Highs touching upper Bollinger Band
data['BB_High'] = np.where((data["High"] >= data["bollinger_up"]),
     data["High"], np.nan)
data["BB_High"] = pd.DataFrame(data["BB_High"])

## Finding lows touching Lower Bollinger Band
data['Swing_Low'] = np.where((data["Low"] <= data["bollinger_down"]),
     data["Low"], np.nan)
data["Swing_Low"] = pd.DataFrame(data["Swing_Low"])


##find the first Non-NAN data before Nan in one column in Pandas
data["Modified1"] = np.append(np.isnan(data["BB_High"].values)[1:], False)
pd.Series(data["BB_High"].values[data["Modified1"]], data["BB_High"].index[data["Modified1"]])
data['Modified_Swing_High'] = np.where((data["Modified1"] == True),
     data["BB_High"], np.nan)
data["Modified_Swing_High"] = pd.DataFrame(data["Modified_Swing_High"])


##find the first Non-NAN data before Nan in one column in Pandas
data["Modified2"] = np.append(np.isnan(data["Swing_Low"].values)[1:], False)
pd.Series(data["Swing_Low"].values[data["Modified2"]], data["Swing_Low"].index[data["Modified2"]])
data['Modified_Swing_Low'] = np.where((data["Modified2"] == True),
     data["Swing_Low"], np.nan)
data["Modified_Swing_Low"] = pd.DataFrame(data["Modified_Swing_Low"])




## Finding the last Swing high among number of Swing Highs just before the Swing Low
Resp_Swing_High = np.argwhere(data["Modified_Swing_Low"].notnull().values).tolist()  ##Removing all Nan values from Modified Swing Low
d = []  ## List of last Swing High among number of Swing Highs just before the Swing Low
Valid_MSH_Value_List = []
Valid_MSH_Date_List = []
Valid_MSH_RSI_List = []
Valid_Index_MSH = None
Valid_MSH = None
Valid_Date_MSH = None
Valid_RSI_MSH = None


for obj in Resp_Swing_High:
    index = obj[0]
    try:
        ## For Exact Swing High
        Valid_Index_MSH = data['Modified_Swing_High'][:index].last_valid_index() ##Finding the last Swing high among number of Swing Highs just before the Swing Low
        Valid_MSH = data["Modified_Swing_High"][Valid_Index_MSH]
        Valid_Date_MSH = data["Datetime"][Valid_Index_MSH]
        Valid_RSI_MSH = data["RSI"][Valid_Index_MSH]
        Valid_MSH_Value_List.append(Valid_MSH)
        Valid_MSH_Date_List.append(Valid_Date_MSH)
        Valid_MSH_RSI_List.append(Valid_RSI_MSH)
        d.append(Valid_Index_MSH)

    except:
        pass

## putting data related with last Swing High among number of Swing Highs just before the Swing Swing Low in PANDAS dataframe
MSH_data = {
    "Valid_MSH": Valid_MSH_Value_List,
    "Datetime": Valid_MSH_Date_List,
    "RSI" : Valid_MSH_RSI_List
}
MSH_df = pd.DataFrame(MSH_data)

b= []
## Converting RSI LIST Data into 4 digit decimal number
for i in range(len( Valid_MSH_RSI_List)):
    c =f'{Valid_MSH_RSI_List[i]:.3f}'[:-1]
    b.append(c)



## converting RSI to string for plotting purpose
# a = [str(x) for x in b] 
# print(a)



#### Finding the last Swing Low among number of Swing Lows just before the Swing High
Resp_Swing_Low = np.argwhere(data["Modified_Swing_High"].notnull().values).tolist()  ##For non-Nan Modified Swing High
valid_MSL_value_list = []
valid_MSL_date_list = []
c = []  ##List of the last Swing Low among number of Swing Highs just before the Swing High
valid_index_MSL = None
valid_MSL = None
valid_date = None

for obj in Resp_Swing_Low:
    index = obj[0]
    try:
        ## For Exact Swing Low
        valid_index_MSL = data['Modified_Swing_Low'][:index].last_valid_index()  ##Finding the last Swing Low among number of Swing Lows just before the Swing High
        valid_MSL = data["Modified_Swing_Low"][valid_index_MSL]
        valid_date_MSL = data["Datetime"][valid_index_MSL]
        valid_MSL_value_list.append(valid_MSL)
        valid_MSL_date_list.append(valid_date_MSL)   
        c.append(valid_index_MSL)

    except:
        pass
## putting data related with last Swing Low among number of Swing Lows just before the Swing High in PANDAS dataframe
MSL_data = {
    "Valid_MSL": valid_MSL_value_list,
    "Datetime": valid_MSL_date_list,
}
MSL_df = pd.DataFrame(MSL_data)



### EXACT SWING LOW
min_value_SL = [] ##List to put the value of minimum LOW between last Swing High and Last Swing Low
min123_SL =[] ##List to put the DATE of value of minimum LOW between last Swing High and Last Swing Low

d = sorted(list(set(d))) ## Sorting the values and removing NAN using SORTED function from List of Last swing high before first swing low
c = sorted(list(set(c))) ## Sorting the values and removing NAN using SORTED function from List of Last swing Low before first swing High


### Exact Swing Low
for i, element in enumerate(d):
    if d[0] > c[0]:
        min_index = None
        if data["Low"][c[i]:d[i]].count() > 2:
            min_index = data["Low"][c[i]:d[i]].idxmin() ## FInding Index of minimum LOW between last Swing High and Last Swing Low
            min_value = data["Low"][min_index]
            date1L = data["Datetime"][min_index]
            min123_SL.append(date1L)
            min_value_SL.append(min_value)

## putting data related with Exact Swing Low in PANDAS dataframe      
t_SL = {
    "t1": min_value_SL,
    "t2": min123_SL,
}
t_SL = pd.DataFrame(t_SL)

## Plotting Exact Swing Low
for i in range(len(t_SL)):
    fplt.add_text((t_SL.loc[i, "t2"], t_SL.loc[i, "t1"]), "Lo", color = "#bb7700")


### Exact Swing High
min_value_SH = [] ##List to put the value of maximum HIGH between last Swing High and Last Swing Low
min123_SH =[] ##List to put the DATE of value of maximum HIGH between last Swing High and Last Swing Low

for i, element in enumerate(d):
    if d[0] > c[0]:
        min_index = None
        if data["High"][c[i]:d[i]].count() > 2:
            min_index = data["High"][c[i]:d[i]].idxmax() ## FInding Index of maximum HIGH between last Swing High and Last Swing Low
            min_value = data["High"][min_index]
            date1L = data["Datetime"][min_index]
            min123_SH.append(date1L)
            min_value_SH.append(min_value)

## putting data related with Exact Swing Low in PANDAS dataframe      
t_SH = {
    "tSH1": min_value_SH,
    "tSH2": min123_SH,
}
t_SH = pd.DataFrame(t_SH)

## Plotting Exact Swing Low
for i in range(len(t_SH)):
    fplt.add_text((t_SH.loc[i, "tSH2"], t_SH.loc[i, "tSH1"]), "Hi", color = "#bb7700")

    


## Plotting candlestick and showing all the Plots
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])

def get_name(Symbol):
    return yf.Ticker(Symbol).info.get("shortName") or Symbol



## To print all DATAS at once
# res.to_csv("any1")
# pd.set_option('display.max_rows', res.shape[0]+1)
# print(res)
# print(res["Modified_Swing_Low"])


# fplt.show(qt_exec = False) # prepares plots when they're all setup
win.show()
app.exec()
fplt.show()

# t_df.to_csv("any1")
# pd.set_option('display.max_rows', data.shape[0]+1)
# print(t_df)










## Downloading financial Data
# data = yf.Ticker("AAPL")
# Balance_Sheet = yf.get_balance_sheet("AAPL")
# b = data.quarterly_balance_sheet
# dividend = data.dividends
# dividend.index = pd.MultiIndex.from_arrays([dividend.index.date,
#     dividend.index.time], names=['Date','Time'])
# dividend = pd.DataFrame(dividend)
# dividend["Datetime"] = dividend.index
# dividend["Date"] = dividend["Datetime"].dt.date
# dividend["Time"] = dividend["Datetime"].dt.time
# print(dividend)


# "My psuh in this"

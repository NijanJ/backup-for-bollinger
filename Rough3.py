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

# Create example charts
combo = QComboBox()
combo.setEditable(True)
[combo.addItem(i) for i in 'AMRK META REVG TSLA TWTR WMT CT=F GC=F ^GSPC ^FTSE ^N225 EURUSD=X ETH-USD'.split()]
dock_0.addWidget(combo, 0, 0, 1, 1)
info = QLabel()
dock_0.addWidget(info, 0, 1, 1, 1)

# Chart for dock_0
ax0,ax1,ax2 = fplt.create_plot_widget(master=area, rows=3, init_zoom_periods=100)
area.axs = [ax0, ax1, ax2]
dock_0.addWidget(ax0.ax_widget, 1, 0, 1, 2)
dock_1.addWidget(ax1.ax_widget, 1, 0, 1, 2)
dock_2.addWidget(ax2.ax_widget, 1, 0, 1, 2)


# Link x-axis
ax1.setXLink(ax0)
ax2.setXLink(ax0)
win.axs = [ax0,ax1,ax2]


# @lru_cache(maxsize = 15)
def download(symbol):
    return yf.download(symbol, "2020-01-01")

# @lru_cache(maxsize = 100)
def get_name(symbol):
    return yf.Ticker(symbol).info.get("shortName") or symbol

def update(txt):
    df = download(txt)
    if len(df) < 20: # symbol does not exist
        return
    info.setText("Loading symbol name...")
    price = df ["Open Close High Low".split()]
    ma20 = df.Close.rolling(20).mean()
    ma50 = df.Close.rolling(50).mean()
    volume = df ["Open Close Volume".split()]
    ax0.reset() # remove previous plots
    ax1.reset() # remove previous plots
    ax2.reset() # remove previous plots
    fplt.candlestick_ochl(price, ax = ax0)
    fplt.plot(ma20, legend = "MA-20", ax = ax1)
    fplt.plot(ma50, legend = "MA-50", ax = ax1)
    fplt.volume_ocv(volume, ax = ax2)
    fplt.refresh() # refresh autoscaling when all plots complete
    Thread(target=lambda: info.setText(get_name(txt))).start() # slow, so use thread

combo.currentTextChanged.connect(update)
update(combo.currentText())

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

## RSI
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



## Finding Highs touching upper Bollinger Band
data['BB_High'] = np.where((data["High"] >= data["bollinger_up"]),
     data["High"], np.nan)
data["BB_High"] = pd.DataFrame(data["BB_High"])

## Finding lows touching Lower Bollinger Band
data['BB_Low'] = np.where((data["Low"] <= data["bollinger_down"]),
     data["Low"], np.nan)
data["BB_Low"] = pd.DataFrame(data["BB_Low"])

##
data["Modified1"] = np.append(np.isnan(data["BB_High"].values)[1:], False)
pd.Series(data["BB_High"].values[data["Modified1"]], data["BB_High"].index[data["Modified1"]])
data['Modified_Swing_High'] = np.where((data["Modified1"] == True),
     data["BB_High"], np.nan)
data["Modified_Swing_High"] = pd.DataFrame(data["Modified_Swing_High"])


##find the first Non-NAN data before Nan in one column in Pandas
data["Modified2"] = np.append(np.isnan(data["BB_Low"].values)[1:], False)
pd.Series(data["BB_Low"].values[data["Modified2"]], data["BB_Low"].index[data["Modified2"]])
data['Modified_Swing_Low'] = np.where((data["Modified2"] == True),
     data["BB_Low"], np.nan)
data["Modified_Swing_Low"] = pd.DataFrame(data["Modified_Swing_Low"])




## Finding the last Swing high among number of Swing Highs just before the Swing Low
Resp_Swing_High = np.argwhere(data["Modified_Swing_Low"].notnull().values).tolist()  ##Removing all Nan values from Modified Swing Low
d = []  ## List of last Swing High among number of Swing Highs just before the Swing Low
Valid_MSH_Value_List = []
Valid_MSH_Date_List = []
Valid_Index_MSH = None
Valid_MSH = None
Valid_Date_MSH = None



for obj in Resp_Swing_High:
    index = obj[0]
    try:
        ## For Exact Swing High
        Valid_Index_MSH = data['Modified_Swing_High'][:index].last_valid_index() ##Finding the last Swing high among number of Swing Highs just before the Swing Low
        Valid_MSH = data["Modified_Swing_High"][Valid_Index_MSH]
        Valid_Date_MSH = data["Datetime"][Valid_Index_MSH]
        Valid_MSH_Value_List.append(Valid_MSH)
        Valid_MSH_Date_List.append(Valid_Date_MSH)
        d.append(Valid_Index_MSH)

    except:
        pass

## putting data related with last Swing High among number of Swing Highs just before the Swing Swing Low in PANDAS dataframe
MSH_data = {
    "Valid_MSH": Valid_MSH_Value_List,
    "Datetime": Valid_MSH_Date_List,
}
MSH_df = pd.DataFrame(MSH_data)





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
min_value_SL_Index = []
min_value_SL = [] ##List to put the value of minimum LOW between last Swing High and Last Swing Low
min123_SL =[] ##List to put the DATE of value of minimum LOW between last Swing High and Last Swing Low

d = sorted(list(set(d))) ## Sorting the values and removing NAN using SORTED function from List of Last swing high before first swing low
c = sorted(list(set(c))) ## Sorting the values and removing NAN using SORTED function from List of Last swing Low before first swing High
del d[0]


Valid_MSH_RSI_List = []
Valid_RSI_MSH = None

Exact_Swing_Low_Index = []
Exact_Swing_Low = [] ##List to put the value of maximum HIGH between last Swing High and Last Swing Low
Exact_Swing_Low_Date =[] ##List to put the DATE of value of maximum HIGH between last Swing High and Last Swing Low

for i, element in enumerate(d):
    # min_index = None
    if d[0] > c[0]:
        if data["Low"][c[i]:d[i]].count() > 2:
            Exact_Swing_Low_Individual_Index = data["Low"][c[i]:d[i]].idxmin() ## FInding Index of minimum LOW between last Swing High and Last Swing Low
    else:
        if data["Low"][c[i]:d[i]].count() > 2:
            Exact_Swing_Low_Individual_Index = data["Low"][d[i]:c[i]].idxmin() ## FInding Index of minimum LOW between last Swing High and Last Swing Low
    
    # print(min_index)
    Exact_Individual_Swing_Low  = data["Low"][Exact_Swing_Low_Individual_Index]
    Exact_Swing_Low_Individual_Date = data["Datetime"][Exact_Swing_Low_Individual_Index]
    Exact_Swing_Low_Index.append(Exact_Swing_Low_Individual_Index)
    Valid_RSI_MSH = data["RSI"][Exact_Swing_Low_Individual_Index]
    Valid_MSH_RSI_List.append(Valid_RSI_MSH)
    Exact_Swing_Low_Date.append(Exact_Swing_Low_Individual_Date)
    Exact_Swing_Low .append(Exact_Individual_Swing_Low)

## putting data related with Exact Swing Low in PANDAS dataframe      
Swing_Low_DF = {
    "Exact_Swing_Low_Index": Exact_Swing_Low_Index,
    "Exact_Swing_Low_Date": Exact_Swing_Low_Date,
    "Exact_Swing_Low" : Exact_Swing_Low,
    "RSI" : Valid_MSH_RSI_List,
}
Swing_Low_DF  = pd.DataFrame(Swing_Low_DF )

## Plotting Exact Swing Low
# for i in range(len(Swing_Low_DF )):
#     fplt.add_text((Swing_Low_DF .loc[i, "Exact_Swing_Low_Date"], Swing_Low_DF .loc[i, "Exact_Swing_Low"]), "Lo", color = "#bb7700")
#     # fplt.add_text((t_SL.loc[i, "RSI"], t_SL.loc[i, "t1"]), Valid_MSH_RSI_List[i], color = "#bb7700")



### Exact Swing High
Exact_Swing_High_Index = []
Exact_Swing_High = [] ##List to put the value of maximum HIGH between last Swing High and Last Swing Low
Exact_Swing_High_Date =[] ##List to put the DATE of value of maximum HIGH between last Swing High and Last Swing Low

for i in range(len(Exact_Swing_Low_Index)):
    # if d[0] > c[0]:
    min_index = None
    if data["High"][Exact_Swing_Low_Index[i-1]:Exact_Swing_Low_Index[i]].count() > 2:
        Exact_Swing_High_Individual_Index = data["High"][Exact_Swing_Low_Index[i-1]:Exact_Swing_Low_Index[i]].idxmax() ## FInding Index of maximum HIGH between last Swing High and Last Swing Low
        Exact_Swing_Individual_High= data["High"][Exact_Swing_High_Individual_Index]
        Exact_Swing_High_Individual_Date = data["Datetime"][Exact_Swing_High_Individual_Index]
        Exact_Swing_High_Index .append(Exact_Swing_High_Individual_Index)
        Exact_Swing_High_Date.append(Exact_Swing_High_Individual_Date)
        Exact_Swing_High.append(Exact_Swing_Individual_High)

## putting data related with Exact Swing Low in PANDAS dataframe      
Swing_High_DF = {
    "Exact_Swing_High_Index" : Exact_Swing_High_Index,
    "Exact_Swing_High_Date": Exact_Swing_High_Date,
    "Exact_Swing_High": Exact_Swing_High,
}
Swing_High_DF = pd.DataFrame(Swing_High_DF)

## Plotting Exact Swing Low
for i in range(len(Swing_High_DF)):
    fplt.add_text((Swing_High_DF.loc[i, "Exact_Swing_High_Date"], Swing_High_DF.loc[i, "Exact_Swing_High"]), "Hi", color = "#bb7700")


### Exact Swing Low
Exact_Swing_Low_Index2 = []
Exact_Swing_Low2 = [] ##List to put the value of maximum HIGH between last Swing High and Last Swing Low
Exact_Swing_Low_Date2 =[] ##List to put the DATE of value of maximum HIGH between last Swing High and Last Swing Low

for i in range(len(Exact_Swing_High_Index)):
    # if d[0] > c[0]:
    min_index = None
    if data["Low"][Exact_Swing_High_Index[i-1]:Exact_Swing_High_Index[i]].count() > 2:
        Exact_Swing_Low_Individual_Index2 = data["Low"][Exact_Swing_High_Index[i-1]:Exact_Swing_High_Index[i]].idxmin() ## FInding Index of maximum HIGH between last Swing High and Last Swing Low
        Exact_Swing_Individual_Low2= data["Low"][Exact_Swing_Low_Individual_Index2]
        Exact_Swing_Low_Individual_Date2 = data["Datetime"][Exact_Swing_Low_Individual_Index2]
        Exact_Swing_Low_Index2.append(Exact_Swing_Low_Individual_Index2)
        Exact_Swing_Low_Date2.append(Exact_Swing_Low_Individual_Date2)
        Exact_Swing_Low2.append(Exact_Swing_Individual_Low2)

## putting data related with Exact Swing Low in PANDAS dataframe      
Swing_Low_DF2 = {
    "Exact_Swing_Low_Index2" : Exact_Swing_Low_Index2,
    "Exact_Swing_Low_Date2": Exact_Swing_Low_Date2,
    "Exact_Swing_Low2": Exact_Swing_Low2,
}
Swing_Low_DF2 = pd.DataFrame(Swing_Low_DF2)

## Plotting Exact Swing Low
for i in range(len(Swing_Low_DF2)):
    fplt.add_text((Swing_Low_DF2.loc[i, "Exact_Swing_Low_Date2"], Swing_Low_DF2.loc[i, "Exact_Swing_Low2"]), "Lo", color = "#bb7700")

    # fplt.add_line((Swing_Low_DF2["Exact_Swing_Low_Date2"][i], Swing_Low_DF2["Exact_Swing_Low2"][i]),
    # (Swing_High_DF["Exact_Swing_High_Date"][i], Swing_High_DF["Exact_Swing_High"][i]), color='#9900ff', interactive=False)

a = Swing_High_DF.duplicated()
print(len(Exact_Swing_Low_Date2))
print(len(Exact_Swing_High_Date))

x = {
    "Exact_Swing_Low_Date2": Exact_Swing_Low_Date2,
    "Exact_Swing_Low2": Exact_Swing_Low2,
    "Exact_Swing_High_Date" : Exact_Swing_High_Date[1:],
    "Exact_Swing_High": Exact_Swing_High[1:],
}
x = pd.DataFrame(x)
print(x)
for i in range(len(x)):
    fplt.add_line((x["Exact_Swing_Low_Date2"][i], x["Exact_Swing_Low2"][i]),
    (x["Exact_Swing_High_Date"][i], x["Exact_Swing_High"][i]), color='#9900ff', interactive=False)

## Plotting Exact Swing Lo}
# print(Swing_High_DF[2:])
# print(len(Swing_High_DF[:]))
# print(len(Swing_Low_DF2[:]))

##Plotting SWING LINES

#     print(Swing_High_DF[Diff1:])
#     print(len(Swing_High_DF[Diff1:]))
# print(Diff1)
# for i in range(len(Swing_High_DF)):
#     # Diff1 = 0
#     if len(Swing_High_DF["Exact_Swing_High_Date"]) > len(Swing_Low_DF["Exact_Swing_Low_Date"]):
#         Diff1 = len(Swing_High_DF["Exact_Swing_High_Date"]) - len(Swing_Low_DF["Exact_Swing_Low_Date"])
#         fplt.add_line((Swing_High_DF[Diff1:]["Exact_Swing_High_Date"][i], Swing_High_DF[Diff1:]["Exact_Swing_High"][i]),
#         (Swing_Low_DF["Exact_Swing_Low_Date"][i], Swing_Low_DF["Exact_Swing_Low"][i]), color='#9900ff', interactive=False)


# Diff2 = 0
# if len(Swing_High_DF["Exact_Swing_High_Date"]) < len(Swing_Low_DF["Exact_Swing_Low_Date"]):
#     Diff2 = len(Swing_Low_DF["Exact_Swing_Low_Date"]) - len(Swing_High_DF["Exact_Swing_High_Date"])
# # for i, element in enumerate(Swing_High_DF):
# print(len(Swing_High_DF))
# # Swing_Low_DF = Swing_Low_DF.drop(labels=range(0, Diff2), axis=0).reset_index()
# # print(len(Swing_High_DF))
# # print(Swing_High_DF)
# for i, element in enumerate(Swing_High_DF):
#     pass
# #     # print(i)
# #     # print(Diff2)
# print(len(Swing_High_DF[:]))
# print(len(Swing_Low_DF[:]))
# print(Swing_High_DF[:])
# print(Swing_Low_DF[:])
# for i in range(len(Swing_Low_DF)):
#     # fplt.add_line((Swing_Low_DF[Diff2:]["Exact_Swing_Low_Date"][i], Swing_Low_DF[Diff2:]["Exact_Swing_Low"][i]),
#     # (Swing_High_DF["Exact_Swing_High_Date"][i], Swing_High_DF["Exact_Swing_High"][i]), color='#9900ff', interactive=False)
#     fplt.add_line((Swing_Low_DF.loc[i, "Exact_Swing_Low_Date"], Swing_Low_DF.loc[i, "Exact_Swing_Low"]),
#     (Swing_High_DF.loc[i, "Exact_Swing_High_Date"], Swing_High_DF.loc[i, "Exact_Swing_High"]), color='#9900ff', interactive=False)

# fplt.add_line((Swing_Low_DF.loc[0, "Exact_Swing_Low_Date"], Swing_Low_DF.loc[0, "Exact_Swing_Low"]),
# (Swing_High_DF.loc[0, "Exact_Swing_High_Date"], Swing_High_DF.loc[0, "Exact_Swing_High"]), color='#9900ff', interactive=False)





    # if Swing_High_DF["Exact_Swing_High_Date"][0] > Swing_Low_DF["Exact_Swing_Low_Date"][0]:
        # fplt.add_line((Swing_High_DF["Exact_Swing_High_Date"][i], Swing_High_DF["Exact_Swing_High"][i]),
        # (Swing_Low_DF[Diff2:]["Exact_Swing_Low_Date"][i], Swing_Low_DF[Diff2:]["Exact_Swing_Low"][i]), color='#9900ff', interactive=False)

# else:
#     for i, element in enumerate(Swing_High_DF):
        # print(i)
#     # if Swing_High_DF["Exact_Swing_High_Date"][0] > Swing_Low_DF["Exact_Swing_Low_Date"][0]:
#         fplt.add_line((Swing_High_DF.loc[i, "Exact_Swing_High_Date"], Swing_High_DF.loc[i, "Exact_Swing_High"]),
#         (Swing_Low_DF.loc[i, "Exact_Swing_Low_Date"], Swing_Low_DF.loc[i, "Exact_Swing_Low"]), color='#9900ff', interactive=False)


#     Swing_Low_DF = Swing_Low_DF.drop(range(0, Diff1))
# else:
#     pass


# print(len(Swing_High_DF["Exact_Swing_High_Date"]))
# print(len(Swing_Low_DF["Exact_Swing_Low_Date"]))
# print(Swing_High_DF["Exact_Swing_High_Date"][0])
# print(Swing_Low_DF["Exact_Swing_Low_Date"][Diff1+1])


# for i in range(len(Swing_Low_DF)):
#     fplt.add_line((Swing_Low_DF.loc[i, "Exact_Swing_Low_Date"], Swing_Low_DF.loc[i, "Exact_Swing_Low"]),
#     (Swing_High_DF.loc[i+1, "Exact_Swing_High_Date"], Swing_High_DF.loc[i+1, "Exact_Swing_High"]), color='#9900ff', interactive=False)



## Plotting candlestick and showing all the Plots
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])

# def get_name(Symbol):
#     return yf.Ticker(Symbol).info.get("shortName") or Symbol



## To print all DATAS at once
# res.to_csv("any1")
# pd.set_option('display.max_rows', res.shape[0]+1)
# print(res)
# print(res["Modified_Swing_Low"])


# fplt.show(qt_exec = False) # prepares plots when they're all setup
win.show()
app.exec()
# fplt.show()

# t_df.to_csv("any1")
# pd.set_option('display.max_rows', data.shape[0]+1)
# print(t_df)











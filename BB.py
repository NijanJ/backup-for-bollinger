from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import yfinance as yf
import finplot as fplt
import numpy as np
import datetime 
from IPython.display import display
import matplotlib as mpl

## Trading Data
tv = TvDatafeed()
data = tv.get_hist(
    symbol='TSLA',exchange='NASDAQ',interval=Interval.in_1_minute,n_bars=5000, fut_contract = 1
)
data = pd.DataFrame(data)

## separateing date and time if datetime is in column not in index
data["datetime"] = data.index
data['date'] = data['datetime'].dt.date
data['time'] = data['datetime'].dt.time
data = data.reset_index(drop=True)


## Bollinger Band formula
def get_sma(prices, rate):
    return prices.rolling(rate).mean()

def get_bollinger_bands(prices, rate=20):
    sma = get_sma(prices, rate)
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return bollinger_up, bollinger_down, sma

## separateing date and time if datetime is index
# data.index = pd.MultiIndex.from_arrays([data.index.date,
#     data.index.time], names=['Date','Time'])


# print(data)


## Removing time from pandas series of date
# a = data["Datetime"].dt.date
# for i in a:
#     b = (data.loc[a]["High"].max())
#     print(i)
#     print(b)



bollinger_up, bollinger_down, sma = get_bollinger_bands(data["close"])
data["bollinger_up"] = bollinger_up
data["bollinger_down"] = bollinger_down
data["SMA"] = sma
# data["SMA"] = sma
# print(data)


# data = data.dropna()
# ax1,ax2,ax3,ax4,ax5 = fplt.create_plot('Bitcoin/Dollar long term analysis', rows=5, maximize=False)
# fplt.set_y_scale(ax=ax1, yscale='log')
# data['ma200'] = data.Close.rolling(20).mean()
# data['ma50'] = data.Close.rolling(50).mean()
# fplt.plot(data.ma200, legend='MA20')
# fplt.plot(data.ma50, legend='MA50', ax=ax1)

## Plot the chart
# fplt.plot(data["Datetime"],data.SMA)
# fplt.plot(data["Datetime"], data["bollinger_up"])
# fplt.plot(data["Datetime"],data["bollinger_down"])
# fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
# fplt.show()


# rows_with_nan = [index for index, row in data.iterrows() if row.isnull().any()]

# print(rows_with_nan)

# # Syntax of enumerate()
# enumerate(data[bollinger_up],start=0)


# data["bollinger_up", ["bollinger_down"], ["SMA"]] = data["bollinger_up", "bollinger_down"], ["SMA"].dropna()

##Swing High

# for i in data:
#     if data.loc(i, "bollinger_up") >= data.loc(i,"High"):
#             data["Swing"] = "SwingHigh"
#             print(data["Swing"])

# data["Swing"] = data.groupby(['High', 'bollinger_up']).apply(data.High >= data.bollinger_up)
data['Swing_High'] = np.where((data["high"] >= data["bollinger_up"]),
     data["high"], np.nan)
data["Swing_High"] = pd.DataFrame(data["Swing_High"])
data['Swing_Low'] = np.where((data["low"] <= data["bollinger_down"]),
     data["low"], np.nan)
data["Swing_Low"] = pd.DataFrame(data["Swing_Low"])

# data = data.dropna()

# data.to_csv("Rough2.csv")

## Plot the chart
fplt.plot(data["datetime"],data["SMA"])
fplt.plot(data["datetime"], data["bollinger_up"])
fplt.plot(data["datetime"],data["bollinger_down"])

## Plotting Swing Highs
# for i in range(len(data)):
#     print(data.loc[i, "Datetime"], data.loc[i, "Swing_High"])
    # fplt.add_text((data.loc[i, "Datetime"], data.loc[i, "Swing_High"]), "H", color = "#bb7700")

## Swing Lows
# for i in range(len(data)):
    # print(data.loc[i, "Datetime"], data.loc[i, "Swing_Low"])
    # fplt.add_text((data.loc[i, "Datetime"], data.loc[i, "Swing_Low"]), "H", color = "#bb7700")





## FInding first Index of non-NAN Swing Low Value

# fplt.add_text((data.loc[First_Swing_Low, "Datetime"], data.loc[First_Swing_Low, "Swing_Low"]), "Low", color = "#bb7700")

## Plotting FIrst Swing High after finding  first index of Swing low

# fplt.add_text((data.loc[First_Swing_High, "Datetime"], data.loc[First_Swing_High, "Swing_High"]), "H", color = "#bb7700")




# ## Next High touching BB

# fplt.add_text((data.loc[Shell_Swing_High, "Datetime"], data.loc[Shell_Swing_High, "Swing_High"]), "H", color = "#bb7700")

# ## Finding Exact Swing Low
# First_Swing_Low = data["High"][First_Swing_High:Shell_Swing_High].idxmin()
# fplt.add_text((data.loc[First_Swing_Low, "Datetime"], data.loc[First_Swing_Low, "Swing_Low"]), "Low", color = "#bb7700")
# print(First_Swing_Low)

# ## Plotting candlestick and showing all the Plots
# fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
# fplt.show()


##Swing High
data["Modified1"] = np.append(np.isnan(data["Swing_High"].values)[1:], False)
pd.Series(data["Swing_High"].values[data["Modified1"]], data["Swing_High"].index[data["Modified1"]])
data['Modified_Swing_High'] = np.where((data["Modified1"] == True),
     data["Swing_High"], np.nan)
data["Modified_Swing_High"] = pd.DataFrame(data["Modified_Swing_High"])

##Swing Low
data["Modified2"] = np.append(np.isnan(data["Swing_Low"].values)[1:], False)
pd.Series(data["Swing_Low"].values[data["Modified2"]], data["Swing_Low"].index[data["Modified2"]])
data['Modified_Swing_Low'] = np.where((data["Modified2"] == True),
     data["Swing_Low"], np.nan)
data["Modified_Swing_Low"] = pd.DataFrame(data["Modified_Swing_Low"])



# data['Swing_Low'] = np.where((data["Low"] <= data["bollinger_down"]),
#      data["Low"], np.nan)
# data["Swing_Low"] = pd.DataFrame(data["Swing_Low"])


# display(data)
# print(data.style)
# print(data["Modified_Swing_High"])

# res = data[data['Modified_Swing_Low'].notnull()]
# print(res)
# resp = np.argwhere(data["Modified_Swing_Low"].notnull().values).tolist()
# valid_MSH_value_list = []
# valid_MSH_date_list = []
# for obj in resp:
#     index = obj[0]
#     valid_index = data["Modified_Swing_High"][:index].last_valid_index()
#     valid_MSH = data["Modified_Swing_High"][valid_index]
#     valid_date = data["datetime"][valid_index]
#     valid_MSH_value_list.append(valid_MSH)
#     valid_MSH_date_list.append(valid_date)
# MSH_data = {
#     "Valid_MSH": valid_MSH_value_list,
#     "Datetime": valid_MSH_date_list
# }
# MSH_df = pd.DataFrame(MSH_data)
# print(MSH_df)
print(data)


## Plotting Swing Highs
# for i in range(len(MSH_df)):
#     # print(data.loc[i, "Datetime"], data.loc[i, "Swing_High"])
#     fplt.add_text((MSH_df.loc[i, "Datetime"], MSH_df.loc[i, "Valid_MSH"]), "Hah", color = "#bb7700")
# # print(First_Swing_Low)
# # ## Plotting candlestick and showing all the Plots
# fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
# fplt.show()


# valid_MSH_dict = {}
# for obj in resp:
#     index = obj[0]
#     valid_index = data['Modified_Swing_High'][:index].last_valid_index()
#     valid_MSH = data["Modified_Swing_High"][valid_index]
#     valid_data = {
#         "Datetime": data["Datetime"][valid_index],
#         "Valid_MSH": valid_MSH
#     }
# valid_MSH_dict.update(valid_data)
# index = [x for x in range(1, len(valid_MSH_dict)+1)]
# MSH_df = pd.DataFrame(index, valid_MSH_dict)

# print(MSH_df)
# MSH_df = pd.DataFrame(MSH_data)
# for i, row in data.iterrows():
# data["a"] = data["Modified_Swing_High"][:res]
# data.to_csv("any")
# pd.set_option('display.max_rows', data.shape[0]+1)
# print(data)








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



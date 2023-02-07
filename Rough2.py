import pandas as pd
import yfinance as yf
import finplot as fplt
import numpy as np
import datetime 
from IPython.display import display
import matplotlib as mpl



## Trading Data
data = yf.download("TSLA", period = "50d", interval = "5m")
data = pd.DataFrame(data)

## separating date and time if datetime is in column not in index
data["Datetime"] = data.index
data['Date'] = data['Datetime'].dt.date
data['Time'] = data['Datetime'].dt.time
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

## separating date and time if datetime is index
# data.index = pd.MultiIndex.from_arrays([data.index.date,
#     data.index.time], names=['Date','Time'])


## Calculating Bollinger Band
bollinger_up, bollinger_down, sma = get_bollinger_bands(data["Close"])
data["bollinger_up"] = bollinger_up
data["bollinger_down"] = bollinger_down
data["SMA"] = sma


## Plot the chart
fplt.plot(data["Datetime"],data["SMA"])
fplt.plot(data["Datetime"], data["bollinger_up"])
fplt.plot(data["Datetime"],data["bollinger_down"])



## Swing High and Swing Lows
# data["Swing"] = data.groupby(['High', 'bollinger_up']).apply(data.High >= data.bollinger_up)
data['Swing_High'] = np.where((data["High"] >= data["bollinger_up"]),
     data["High"], np.nan)
data["Swing_High"] = pd.DataFrame(data["Swing_High"])
data['Swing_Low'] = np.where((data["Low"] <= data["bollinger_down"]),
     data["Low"], np.nan)
data["Swing_Low"] = pd.DataFrame(data["Swing_Low"])



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


print(data)

# res = data[data['Modified_Swing_Low'].notnull()]
# res.reset_index(inplace=True)
# res = res.rename(columns = {'index':'final'})

##Convert Strings to Integers in Pandas DataFrame
# res = res['final'].astype(int)
# valid_MSH_value_list = []
# valid_MSH_date_list = []
# for obj in res:
#     u = data["Modified_Swing_High"].loc[:res+1].last_valid_index()
#     v = data["Modified_Swing_High"][u]
#     x = data["Datetime"][u]
#     valid_MSH_value_list.append(v)
#     valid_MSH_date_list.append(x)

# a = pd.DataFrame(list(zip(valid_MSH_value_list, valid_MSH_date_list)),columns=['lst1_title','lst2_title'])

# print(a)

res.to_csv("any1")
pd.set_option('display.max_rows', res.shape[0]+1)
print(res)
print(res["Modified_Swing_Low"])


## Fror exact Swing High
Resp_Swing_High = np.argwhere(data["Modified_Swing_Low"].notnull().values).tolist()  ##For Swing High
valid_MSH_value_list = []
valid_MSH_date_list = []
valid_index_MSH = None
valid_MSH = None
valid_date_MSH = None


for obj in Resp_Swing_High:
    index = obj[0]
    try:
        ## For Exact Swing High
        valid_index_MSH = data['Modified_Swing_High'][:index].last_valid_index()
        valid_MSH = data["Modified_Swing_High"][valid_index_MSH]
        valid_date_MSH = data["Datetime"][valid_index_MSH]
        valid_MSH_value_list.append(valid_MSH)
        valid_MSH_date_list.append(valid_date_MSH)

    except:
        pass

## For Exact Swing High
MSH_data = {
    "Valid_MSH": valid_MSH_value_list,
    "Datetime": valid_MSH_date_list,
}
MSH_df = pd.DataFrame(MSH_data)


## Fror exact Swing Low
Resp_Swing_Low = np.argwhere(data["Modified_Swing_High"].notnull().values).tolist()  ##For Swing Low
valid_MSL_value_list = []
valid_MSL_date_list = []
valid_index_MSL = None
valid_MSL = None
valid_date = None

for obj in Resp_Swing_Low:
    index = obj[0]
    try:
        ## For Exact Swing Low
        valid_index_MSL = data['Modified_Swing_Low'][:index].last_valid_index()
        valid_MSL = data["Modified_Swing_Low"][valid_index_MSL]
        valid_date_MSL = data["Datetime"][valid_index_MSL]
        valid_MSL_value_list.append(valid_MSL)
        valid_MSL_date_list.append(valid_date_MSL)   

    except:
        pass

## For Exact Swing Low
MSL_data = {
    "Valid_MSL": valid_MSL_value_list,
    "Datetime": valid_MSL_date_list,
}
MSL_df = pd.DataFrame(MSL_data)
print(MSL_df)



# # Plotting EXACT Swing Highs 
for i in range(len(MSH_df)):
    # print(data.loc[i, "Datetime"], data.loc[i, "Swing_High"])
    fplt.add_text((MSH_df.loc[i, "Datetime"], MSH_df.loc[i, "Valid_MSH"]), "Hi", color = "#bb7700")


# # Plotting EXACT Swing Lows
for i in range(len(MSL_df)):
    fplt.add_text((MSL_df.loc[i, "Datetime"], MSL_df.loc[i, "Valid_MSL"]), "Lo", color = "#bb7700")



## Plotting candlestick and showing all the Plots
fplt.candlestick_ochl(data[["Datetime","Open", "Close", "High", "Low"]])
fplt.show()











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



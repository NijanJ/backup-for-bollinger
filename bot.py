# import yfinance as yf
# import pandas as pd
# import time
# print("a")
# # Get the stock information
# historical_data = yf.download("HDFC.NS", period="5d", interval = "1m")
# # print(stock)
# # Get the historical data of the stock
# # historical_data =yf.download("HDFC.NS", period="5d", interval = "1m")

# # Define the interval in seconds to update the data
# interval = 60 # 1 minute

# # Continuously update the data
# while True:
#     # Get the latest data of the stock
#     new_data = yf.download("HDFC.NS", period="5d", interval = "1m")

#     # Update the historical data with the latest data
#     historical_data = pd.concat([historical_data, new_data]).drop_duplicates().sort_index()
#     print("a")

#     # Sleep for the specified interval
#     time.sleep(interval)
#     print("a")

# #     print(new_data)

# # import yfinance as yf
# # import pandas as pd
# # import time

# # # Get the stock information
# # stock = yf.Ticker("HDFC.NS")

# # # Define the interval in seconds to update the data
# # interval = 60 # 1 minute

# # # Get the entire historical data
# # historical_data = stock.history(period="5d", interval="1m")

# # # Continuously update the data
# # while True:
# #     # Get the latest data of the stock
# #     new_data = stock.history(period="1d", interval="1m")

# #     # Check if the latest data already exists in the historical data
# #     latest_date = new_data.index[-1]
# #     if latest_date not in historical_data.index:
# #         # Update the historical data with only the latest data
# #         historical_data = pd.concat([historical_data, new_data])

# #     # Save the historical data to a file
# #     historical_data.to_csv("historical_data.csv", index=True)
# #     print("BHOSDIKE")
# #     # Sleep for the specified interval
# #     time.sleep(interval)
   

    
# # import yfinance as yf
# # import pandas as pd
# # import time

# # # Download historical data once at the beginning
# # ticker = "HDFC.NS"
# # df = yf.download(ticker, period="5d", interval="1m")

# # # Continuously update the data every 1 minute
# # while True:
# #     # Get the latest data
# #     latest_data = yf.download(ticker, period="5d", interval="1m")
# #     if latest_data.empty:
# #         print("No new data available.")
# #     else:
# #         # Append the latest data to the existing data
# #         df = df.append(latest_data)
# #         print(df)
# #         print("Data updated.")
# #         print("LODU")
# #     time.sleep(60)

# import yfinance as yf
# import pandas as pd
# import time

# # Get the stock information
# stock = yf.Ticker("AAPL")

# # Get the entire historical data of the stock
# historical_data = stock.history(period="5d", interval="1m")

# # Save the historical data to file
# historical_data.to_csv("historical_data.csv", index=False)

# # Define the interval in seconds to update the data
# interval = 60 # 1 minute

# # Continuously update the data
# while True:
#     # Get the latest data of the stock
#     new_data = stock.history(start=historical_data.index[-1], period="1d", interval="1m")

#     # Check if there is any new data
#     if not new_data.empty:
#         # Update the historical data with the latest data
#         historical_data = pd.concat([historical_data, new_data]).sort_index()

#         # Save the updated historical data to file
#         historical_data.to_csv("historical_data.csv", index=False)
#         print("BHOSDIKE")
#         print(historical_data)

#     # Sleep for the specified interval
#     time.sleep(interval)
#     print(historical_data)


# import finplot as fplt
# import random
# import time

# def generate_data():
#     while True:
#         yield random.random()

# fplt.show()

# data = generate_data()
# fplt.candlestick_ochl(next(data), next(data), next(data), next(data))

# while True:
#     fplt.candlestick_ochl(next(data), next(data), next(data), next(data), append=True)
#     time.sleep(1)
# import finplot as fplt
# import random
# import time

# def generate_data():
#     while True:
#         yield random.random()

# data = generate_data()
# x, open_, close, high, low = [0], next(data), next(data), next(data), next(data)
# fplt.candlestick_ochl(x, [open_, close, high, low])
# fplt.show()

# while True:
#     x.append(x[-1] + 1)
#     open_.append(next(data))
#     close.append(next(data))
#     high.append(next(data))
#     low.append(next(data))
#     fplt.candlestick_ochl(x, open_, close, high, low)
#     time.sleep(1)
import finplot as fplt
import random
import time

def generate_data():
    while True:
        yield random.random()

data = generate_data()
x = [0, 1, 2, 3, 4, 5,6,7,8]
open_ = [next(data) for _ in x]
close = [next(data) for _ in x]
high = [next(data) for _ in x]
low = [next(data) for _ in x]
ax = fplt.create_plot()
fplt.candlestick_ochl([x,open_, close, high, low], ax=ax)
fplt.show()

while True:
    x = [i + 5 for i in x]
    open_ = [next(data) for _ in x]
    close = [next(data) for _ in x]
    high = [next(data) for _ in x]
    low = [next(data) for _ in x]
    fplt.candlestick_ochl([x, open_, close, high, low], ax=ax)
    time.sleep(10)


import yfinance as yf
import pandas as pd
import time

# Get the stock information
stock = yf.Ticker("AAPL")
historical_data = stock.history(period="5d", interval="1m")
historical_data.to_csv("historical_data.csv")

# Define the interval in seconds to update the data
interval = 60 # 1 minute

# Continuously update the data
while True:
    # Get the latest data of the stock
    new_data = stock.history(period="1d", interval="1m")

    # Check if the historical data file exists
    try:
        with open("historical_data.csv") as file:
            historical_data = pd.read_csv(file)
    except FileNotFoundError:
        # Create the historical data file if it does not exist
        historical_data = pd.DataFrame(columns=new_data.columns)

    # Check if the latest data already exists in the historical data
    latest_date = new_data.index[-1]
    if latest_date not in historical_data.index:
        # Update the historical data with the latest data
        historical_data = pd.concat([historical_data, new_data]).sort_index()

        # Save the updated historical data to file
        historical_data.to_csv("historical_data.csv", index=False)

    # Sleep for the specified interval
    time.sleep(interval)

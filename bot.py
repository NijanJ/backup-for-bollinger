# import yfinance as yf
# import pandas as pd
# import time
# print("a")
# # Get the stock information
# stock = yf.Ticker("AAPL")

# # Get the historical data of the stock
# historical_data = stock.history(period="5d", interval = "1m")

# # Define the interval in seconds to update the data
# interval = 60 # 1 minute

# # Continuously update the data
# while True:
#     # Get the latest data of the stock
#     new_data = stock.history(period="1d" ,interval = "1m")

#     # Update the historical data with the latest data
#     historical_data = pd.concat([historical_data, new_data]).drop_duplicates().sort_index()

#     # Sleep for the specified interval
#     time.sleep(interval)

#     print(new_data)

import yfinance as yf
import pandas as pd
import time

# Get the stock information
stock = yf.Ticker("AAPL")

# Define the interval in seconds to update the data
interval = 60 # 1 minute

# Continuously update the data
while True:
    # Get the latest data of the stock
    new_data = stock.history(start=None, end=None, interval="1d")

    # Check if the latest data already exists in the historical data
    latest_date = new_data.index[-1]

    # Load the historical data from a file
    try:
        historical_data = pd.read_csv("historical_data.csv", index_col=0, parse_dates=True)
        old_latest_date = historical_data.index[-1]
    except FileNotFoundError:
        old_latest_date = None

    # Check if the latest data is newer than the existing data
    if old_latest_date is None or latest_date > old_latest_date:
        # Save only the latest data to the file
        new_data.iloc[[-1]].to_csv("historical_data.csv")

    # Sleep for the specified interval
    time.sleep(interval)

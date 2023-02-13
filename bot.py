import yfinance as yf
import pandas as pd
import time
print("a")
# Get the stock information
stock = yf.Ticker("AAPL")

# Get the historical data of the stock
historical_data = stock.history(period="5d", interval = "1m")

# Define the interval in seconds to update the data
interval = 60 # 1 minute

# Continuously update the data
while True:
    # Get the latest data of the stock
    new_data = stock.history(period="1d" ,interval = "1m")

    # Update the historical data with the latest data
    historical_data = pd.concat([historical_data, new_data]).drop_duplicates().sort_index()

    # Sleep for the specified interval
    time.sleep(interval)

    print(new_data)


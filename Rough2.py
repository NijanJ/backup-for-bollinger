import talib
import numpy as np

# Define data
close_prices = np.array([10.5, 11.0, 10.75, 11.25, 11.5, 12.0, 11.75, 11.25, 11.0])

# Check if input data is valid
if len(close_prices) < 26:
    print("Error: Not enough data points for MACD calculation")
else:
    # Calculate MACD
    macd, macdsignal, macdhist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)

    # Print results
    print("MACD:", macd)
    print("MACD Signal:", macdsignal)
    print("MACD Histogram:", macdhist)

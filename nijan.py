import finplot as fplt
import pandas as pd
import time
import random
import numpy as np


import finplot as fplt
import pandas as pd
import random

# create an empty DataFrame to hold the live data
data = pd.DataFrame(columns=['time', 'price'])

# create a finplot figure
fig = fplt.create_plot()

# create a line plot for the price data
fplt.plot(data['time'], data['price'], color='#0080ff')
fplt.legend('Price')

# add a simple moving average indicator
sma_period = 10
sma = data['price'].rolling(sma_period).mean()
sma_plot = fplt.add_line(data['time'], sma, color='#ff8000', label=f'SMA ({sma_period})')

# define a function to generate random data
def generate_data():
    while True:
        yield pd.DataFrame({
            'time': pd.Timestamp.now(),
            'price': random.uniform(90, 110)
        }, index=[0])

# create a generator for the data
data_gen = generate_data()

# define a function to update the plot
def update_plot():
    # get the latest data point
    new_data = next(data_gen)
    
    # append it to the DataFrame
    data.loc[len(data)] = new_data.loc[0]
    
    # update the price plot
    price_plot.update(data['time'], data['price'])
    
    # update the SMA plot
    sma = data['price'].rolling(sma_period).mean()
    sma_plot.update(data['time'], sma)

# schedule the update function to be called every 1 second
fplt.timer_callback(update_plot, 1.0)

# show the plot
fplt.show()

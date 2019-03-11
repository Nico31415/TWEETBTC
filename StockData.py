from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import datetime



#datetime.datetime is a datatype within the datetime module
start_date = datetime.datetime(2016,1,1)
end_date = datetime.datetime(2019,1,1)

#DataReader method name is case sensitive
BTC = data.DataReader('BTC-USD', 'yahoo', start_date, end_date)
ETH = data.DataReader('ETH-USD', 'yahoo', start_date, end_date)
#invoke to_csv for df dataframe object from
#DataReader method in the pandas_datareader library

#..\first_yahoo_prices_to_csv_demo.csv msutnot be open in another app
# such as Excel

BTC = BTC.drop("High", axis = 1)
BTC = BTC.drop("Low", axis = 1)
BTC = BTC.drop("Open", axis = 1)
BTC = BTC.drop("Close", axis = 1)
BTC = BTC.drop("Volume", axis = 1)

ETH = ETH.drop("High", axis = 1)
ETH = ETH.drop("Low", axis = 1)
ETH = ETH.drop("Open", axis = 1)
ETH = ETH.drop("Close", axis = 1)
ETH = ETH.drop("Volume", axis = 1)


BTC.to_csv('BtcPrices2.csv')
ETH.to_csv('EthPrices2.csv')

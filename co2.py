import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)#reads text file and stores as a dataframe
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])#converts all of the date/time stuff to a single variable type
boolMissing=dfCarbonDioxide['value']==-999.99#boolean filter for missing data
dfCarbonDioxide[boolMissing]=np.nan#using boolean filter to take out missing values
dfCarbonDioxide=dfCarbonDioxide.dropna()#drops missing values
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)#renumbers the dataframe index without the dropped values

#makes a plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
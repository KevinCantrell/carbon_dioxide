import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#reads file and stores it as pd dataframe
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
#converts date and time data into datetime format
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#boolean filter for missing data
boolMissing=dfCarbonDioxide['value']==-999.99
#makes missing data non values
dfCarbonDioxide[boolMissing]=np.nan
#elliminates missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#elliminates rows that had missing data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#makes plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
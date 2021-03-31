import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

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

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
fitCO2=fitPly(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
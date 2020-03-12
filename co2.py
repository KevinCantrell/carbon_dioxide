import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def polyFunc(x, c0, c1, c2): 
    return c0 + (x*c1) + ((x ** 2) * c2)
#begin actual code ------------------------------------------------------------
    
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=146)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)
print(dfCarbonDioxide)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')


startDate=min(dfCarbonDioxide['date'])

#this is a pandas series, aka just a single column with named rows
#the returned data type is a time delta, aka num of days passed but not actualy a float
timeElapsed=dfCarbonDioxide['date']-startDate
#no longer a datetime, but a float, which we can actually use in calculations
#days since start is the x value
daysSinceStart=timeElapsed.dt.days


#creating straight line fit, second order -------------------------------------
coefs  = np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)

predicted = polyFunc(daysSinceStart, coefs[2], coefs[1], coefs[0])

#this is what's left after we attempt to fit to a polynomal
#this will help us with determining the values for a oscillating fit
fit, axResidual = plt.subplots()
axResidual.plot(dfCarbonDioxide['date'], (dfCarbonDioxide['value'] - predicted), '-r')


import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def CDfunc(x, y1, y2, y3):
    
    CD = y1*(x**2)+(y2*x)+y3
    return CD

dfCD=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCD['date']=pd.to_datetime(dfCD[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCD['value']==-999.99
dfCD[boolMissing]=np.nan
dfCD=dfCD.dropna()
dfCD=dfCD.reset_index(drop=True)

#dates from start, adjusts x-axis based on this value
startD=min(dfCD['date'])
timeElapsed=dfCD['date']-startD
dSStart=timeElapsed.dt.days

#plots stuff
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCD['date'],dfCD['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

# want a second-order polynomial
#using scipy optimize.curve_fit
CD_Pfit= np.polyfit(dSStart,dfCD['value'],2)

CD_calc = CDfunc(dSStart,CD_Pfit[0],CD_Pfit[1],CD_Pfit[2])

#CD_Cfit= curve_fit(CDfunc, dfCD['date'], dfCD['value'] )

#plot
#red line
ax.plot(dfCD['date'], CD_calc, '-r')

#ax.plot(dfCD['date'], CD_Cfit, '-g')

#difference between red line and black points - next week
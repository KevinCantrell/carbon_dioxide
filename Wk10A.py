import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

def fitOsc(x,amp,period,offset):
    y=amp/2*np.cos((x+offset)*2*np.pi/period)
    return y

def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y                

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#creating figure
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days


fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
#popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'])
poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
#fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
fitCO2=fitAll(daysSinceStart,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
        
res=fitCO2-dfCarbonDioxide['value']
figRes,axRes=plt.subplots()
axRes.plot(daysSinceStart,res)

stdErr=np.sqrt(np.sum(res**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))

oscCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,oscCalc)

#predicting levels in May
dateToPredict=pd.to_datetime('2021-04-08 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
predictedCO2=fitAll(daysSinceStartPrediction,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(dateToPredict,predictedCO2,'og')
print(daysSinceStartPrediction)


#predicts years in the future
daysFuture=np.linspace(0,int(np.ceil(365.25*50)),int(np.ceil(365.25*50)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture,unit='d') 
futureCO2=fitAll(daysFuture,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(datesFuture,futureCO2,'-r')




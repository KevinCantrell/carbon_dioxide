import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

def fitPly3(x,c3,c2,c1,c0):
    y=x**3*c3+x**3*c2+x*c1+c0
    return y

def fitOsc(x,amp,period,offset):
    y=amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
    #y=amp*np.cos(period*(x+offset))
    return y

#def fitAll(x,c2,c1,c0,amp,period,offset):
    #y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
   # return y
def fitAll(x,c3,c2,c1,c0,amp,period,offset):
    y=fitPly3(x,c3,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y

def fitPart(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y
    
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#make a plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
fitCO2=fitPly(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

fitCoeffs3=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],3)
poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs3[0],fitCoeffs3[1],fitCoeffs3[2],fitCoeffs3[3],8,365.25,200])
poptPart,pcov=curve_fit(fitPart,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
#poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=fitCoeffs3[0],fitCoeffs[1],fitCoeffs3[2],fitCoeffs3[3],8,365.25,200 )
#fitCO2Ply=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
#ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

fitCO2ply=fitPly(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2])
fitCO2all=fitAll(daysSinceStart,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5],poptAll[6])
fitCO2part=fitPart(daysSinceStart,poptPart[0],poptPart[1],poptPart[2],poptPart[3],poptPart[4],poptPart[5])

ax.plot(dfCarbonDioxide['date'],fitCO2all,'-r')
ax.plot(dfCarbonDioxide['date'],fitCO2ply,'-b')
ax.plot(dfCarbonDioxide['date'],fitCO2part,'-g')

residualsAll=fitCO2all-dfCarbonDioxide['value']
residualsPart=fitCO2part-dfCarbonDioxide['value']
residualsPly=fitCO2ply-dfCarbonDioxide['value']

figRes,axRes=plt.subplots(figsize=(12,8))
axRes.plot(daysSinceStart,residualsAll,'-r')
axRes.plot(daysSinceStart,residualsPly,'-b')
axRes.plot(daysSinceStart,residualsPart,'-g')
#axRes.plot(dfCarbonDioxide['date'],residuals)
#stdError=np.sqrt(np.sum(residuals**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))
#pyplOscillationCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,OscillationCalc)

rss1=np.sum(residualsPart**2)
rss2=np.sum(residualsAll**2)
p1=len(poptPart)
p2=len(poptAll)
n=len(dfCarbonDioxide['value'])
fcalc=((rss1-rss2)/(p2-p1))/(rss2/(n-p2))
fTable=stats.f.ppf(1-(0.05),p2-p1,n-p2)

stdErrorAll=np.sqrt(np.sum(residualsAll**2)/(len(dfCarbonDioxide['value'])-len(poptAll)))
stdErrorPly=np.sqrt(np.sum(residualsPly**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))
stdErrorPart=np.sqrt(np.sum(residualsPart**2)/(len(dfCarbonDioxide['value'])-len(poptPart)))

dateToPredict=pd.to_datetime('2021-04-08 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
print(daysSinceStartPrediction)
predictedCO2=fitAll(daysSinceStartPrediction,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5],poptAll[6])


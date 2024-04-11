import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def CalcCO2Poly(days,c2,c1,c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

def cosCalcCO2(days,amp,off,frq):
    sinu=amp/2 * np.cos((days + off)  * 2 * np.pi/frq)
    return sinu

def CalcCO2Full(days, c2,c1,c0,amp,off,frq):
    co2calc=CalcCO2Poly(days,c2,c1,c0)+cosCalcCO2(days,amp,off,frq)
    return co2calc
    
dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#converts time data into one parameter pandas datetime
boolMissing=dfCarbonDioxide['value']==-999.99
#-999.99 means didn't get good data that day
dfCarbonDioxide[boolMissing]=np.nan
#nan is pandas centinal value for missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#dropna gets rid of nan sets from dataframe
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)
#reindexes data


#goal is to model data with scipy curv fit to predict future
#turn data into number fisrt
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
#calculate time elapsed by subtracting minimum/start date
daysSinceStart=timeElapsed.dt.days
#gives number of days since start, x values

fitpoly=np.polyfit(daysSinceStart,dfCarbonDioxide['value'], 2)
#second order fit

co2fitPoly=CalcCO2Poly(daysSinceStart,fitpoly[0],fitpoly[1],fitpoly[2])

# xdata=np.linespace(np.min(daysSinceStart),np.max(daysSinceStart)+100,1000)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
#uses a date format for x axis

y=dfCarbonDioxide['value']
yfit=co2fitPoly
res=y-yfit
n=len(daysSinceStart)
df=n-(len(fitpoly))
sy=np.sqrt(np.sum(res**2) / df )

sinuCO2fit=cosCalcCO2(daysSinceStart,9,0,365)
#frq is one year, 140 x of first peak


# figRes, axRes = plt.subplots(figsize=(12,8))
# axRes.plot(daysSinceStart,res,'.k')
# axRes.plot(daysSinceStart, sinuCO2fit,'-r')

co2fitfull=CalcCO2Full(daysSinceStart,fitpoly[0],fitpoly[1],fitpoly[2],9,0,365)
# ax.plot(dfCarbonDioxide['date'], co2fitfull,'-g')

popt,pcov=curve_fit(CalcCO2Full, daysSinceStart, dfCarbonDioxide['value'],p0=[fitpoly[0],fitpoly[1],fitpoly[2],9,0,365])
curverrors=(np.sqrt(np.diag(pcov)))
c2opt=popt[0]
c1opt=popt[1]
c0opt=popt[2]
ampopt=popt[3]
offopt=popt[4]
frqopt=popt[5]

dateToPredict=pd.to_datetime('2024-03-29 00:00:00')
dateGrad=pd.to_datetime('2024-05-05 00:00:00')
dayToPredict=dateToPredict-startDate
dayToGrad=dateGrad-startDate
daysSinceStartPrediction=dayToPredict.days
daysSinceStartGrad=dayToGrad.days
yearToPredict=dateToPredict.year+dateToPredict.day_of_year/(365+dateToPredict.is_leap_year)
daysFuture=np.linspace(0,int(np.ceil(365.25*52)),int(np.ceil(365.25*52)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='d')
yearToGrad=dateGrad.year+dateGrad.day_of_year/(365+dateGrad.is_leap_year)
datesGrad=startDate+pd.to_timedelta(dayToGrad, unit='d')
Grad=datesGrad.strftime('%B-%d-%Y')
co2err="{:.1E}".format(sy)

CO2curveOpt=CalcCO2Full(daysSinceStart,c2opt,c1opt,c0opt,ampopt,offopt,frqopt)
CO2curvePredict=CalcCO2Full(daysSinceStartPrediction,c2opt,c1opt,c0opt,ampopt,offopt,frqopt)
CO2curveFuture=CalcCO2Full(daysFuture,c2opt,c1opt,c0opt,ampopt,offopt,frqopt)
CO2Grad=CalcCO2Full(daysSinceStartGrad,c2opt,c1opt,c0opt,ampopt,offopt,frqopt)
CO2Gradstr="{:.3E}".format(CO2Grad)

# ax.plot(dfCarbonDioxide['date'],CO2curveOpt, '-r')
ax.plot(datesFuture,CO2curveFuture,color='#54e441')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_ylabel('$CO_2$ (ppm)')
ax.set_xlabel('Date')
# ax.text('Predicted $CO_2$ on''is''ppm')
ax.annotate('Predicted $CO_2$ on ' + Grad +' is ' + CO2Gradstr + ' ($ \pm$'+ co2err + ') ppm',xy=(datesGrad, CO2Grad),xycoords='data',xytext=(0.25, 0.85),  textcoords='axes fraction',arrowprops={'color':'black', 'width':1, 'headwidth':5},bbox={'boxstyle':'round', 'edgecolor':'#FD6C9E','facecolor':'0.8'})
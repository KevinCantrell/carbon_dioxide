import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def CalcCO2Poly(days,c2,c1,c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

def CalcCO2Osc(days,amp,offset,period):# amplitude, time takes to get to peak (how many days), distance between two peaks
    return amp/2*np.cos((days+offset)*2*np.pi/period)

def CalcCO2Full(days,c2,c1,c0,amp,offset,period):
    co2calc=CalcCO2Poly(days,c2,c1,c0)+CalcCO2Osc(days,amp,offset,period)
    return co2calc

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99 #creates filter true for bad data 
dfCarbonDioxide[boolMissing]=np.nan #filter all missing data or -999.99
dfCarbonDioxide=dfCarbonDioxide.dropna() #drop all 'missing' data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

#peak in april and may and min at october
#monoloa

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitPoly= np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)

co2fitPoly=CalcCO2Poly(daysSinceStart,fitPoly[0],fitPoly[1],fitPoly[2])
#ax.plot(dfCarbonDioxide['date'],co2fitPoly,'-r')

res=-co2fitPoly+dfCarbonDioxide['value']
figRes,axRes=plt.subplots()
axRes.plot(daysSinceStart,res)

resFit=CalcCO2Osc(daysSinceStart, 9,0,365)
axRes.plot(daysSinceStart,resFit)

co2fitFull=CalcCO2Full(daysSinceStart,fitPoly[0],fitPoly[1],fitPoly[2],9,0,365)
ax.plot(dfCarbonDioxide['date'],co2fitFull,'-g')

CO2P,CO2C=curve_fit(CalcCO2Full,daysSinceStart,dfCarbonDioxide['value'],p0=[fitPoly[0],fitPoly[1],fitPoly[2],9,0,365])
CO2calc=CalcCO2Full(daysSinceStart, CO2P[0], CO2P[1], CO2P[2], CO2P[3],CO2P[4], CO2P[5])
ax.plot(dfCarbonDioxide['date'],CO2calc,'-m')


dateToPredict=pd.to_datetime('2024-03-29 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
CO2calcPrediction=CalcCO2Full(daysSinceStartPrediction, CO2P[0], CO2P[1], CO2P[2], CO2P[3],CO2P[4], CO2P[5])

daysFuture=np.linspace(0,int(daysSinceStartPrediction+(365.25*3)),int(daysSinceStartPrediction+(365.25*3)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture,unit='d')
CO2calcFuture=CalcCO2Full(daysFuture, CO2P[0], CO2P[1], CO2P[2], CO2P[3],CO2P[4], CO2P[5])
ax.plot(datesFuture,CO2calcFuture,'-c')

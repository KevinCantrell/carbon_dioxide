import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def PolyReg(x,y,order=1): 
    n=len(x)
    df=n-(1+order) #number of data points minus the order plus 1
    coefs,cov=np.polyfit(x,y,order,cov=True)
    errors=np.sqrt(np.diagonal(cov))
    poly=np.poly1d(coefs)
    yFit=poly(x)
    res=yFit-y
    sy=np.sqrt(sum(res**2)/df)
    return{'coefs':coefs,'errors':errors,'sy':sy,'n':n,'poly':poly,'res':res,'df':df, 'yFit':yFit, 'slope':coefs[-2], 'intercept':coefs[-1], 'errM':errors[-2], 'errB':errors[-1]}

def CO2Func(days,C2,C1,C0,n,A,p):
    CO2=C2*days**2+C1*days+C0+A/2*np.cos(((days+n)*2*np.pi)/p)
    return CO2    

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158) #reading the data from a txt file and letting it know what to skip and how different data is notated
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']]) #reading the date data only
boolMissing=dfCarbonDioxide['value']==-999.99 #starting to get rid of n/a data
dfCarbonDioxide[boolMissing]=np.nan #replacing data with n/a
dfCarbonDioxide=dfCarbonDioxide.dropna() #telling the script to reomve n/a data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True) #finalizing the data

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days
endDate=pd.to_datetime(2025,5,4,0,0,0)
endPredic=endDate-startDate


fit1=PolyReg(daysSinceStart,dfCarbonDioxide['value'],2)
C2=fit1['coefs'][0]
C1=fit1['coefs'][1]
C0=fit1['coefs'][2]
offSet=200
Amp=5
Per=300
yFit=CO2Func(daysSinceStart,C2,C1,C0,offSet,Amp,Per)


fig,ax = plt.subplots(figsize=(12,8)) #making a figure
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k') #plotting the known data as black small points
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d') #formating the dates to be consitent
ax.plot(dfCarbonDioxide['date'],yFit,'r')
ax.set_ylabel('$CO_2$ Concentration (ppm)')
ax.set_xlabel('Date')
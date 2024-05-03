import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def oscFunc(x, amp, offset, period):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def plyFunc(x,c0,c1,c2):
    return c0+x*c1+x**2*c2

def fitFull (x,c2,c1,c0,amp,offset,period):
    result = oscFunc(x,amp,offset,period)+plyFunc(x,c0,c1,c2)
    return result

def CO2All(xdata,c2,c1,c0,amp,offset,period):
    return CO2func(xdata,c2,c1,c0)+oscFunc(xdata,amp,offset,period)

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days
xdata=daysSinceStart

# fitCO2Parameters=np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)
# fitCO2=fitFull(daysSinceStart,fitCO2Parameters[0],fitCO2Parameters[1],fitCO2Parameters[2],10,0,365)
# curvefitCO2=curve_fit(fitCO2,daysSinceStart,dfCarbonDioxide['value'])

popt, pcov=curve_fit(plyFunc,xdata,dfCarbonDioxide['value'])
c2=popt[0]
c1=popt[1]
c0=popt[2]

concCO2=plyFunc(xdata,c2,c1,c0)
ax.plot(dfCarbonDioxide['date'],concCO2,"-r")

dateToPredict=pd.to_datetime('2023-04-12 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
print(daysSinceStartPrediction)

daysFuture=np.linspace(0,int(np.ceil(365.25*50)),int(np.ceil(365.25*50)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='d')

popt2, pcov2=curve_fit(CO2All,xdata,dfCarbonDioxide['value'],p0=[c2,c1,c0,9,0,365])
errors=np.sqrt(np.diag(pcov2))

c2=popt2[0]
c1=popt2[1]
c0=popt2[2]
amp=popt2[3]
offset=popt2[4]
period=popt2[5]

c2e=errors[0]
c1e=errors[1]
c0e=errors[2]
ampe=errors[3]
offsete=errors[4]
periode=errors[5]

predictedCO2whole=CO2All(daysFuture,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])
ax.plot(datesFuture,predictedCO2whole,"-r")
predictedCO2=CO2All(daysSinceStartPrediction,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])
orderedCoefs=[c0,c1,c2,amp,offset,period]
orderedErrors=[c0e,c1e,c2e,ampe,offsete,periode]
stdErrorFit=np.sqrt(np.sum((concCO2osc-dfCarbonDioxide['value'])**2)/(len(concCO2osc)-len(popt2)))
residuals=(concCO2osc-dfCarbonDioxide['value'])

fit={'coefs':orderedCoefs,'errors':orderedErrors,'sy':stdErrorFit,'n':len(concCO2osc),'res':residuals,'labels':['initial','linear','exp','amplitude','offset','period','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)
annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(predictedCO2,stdErrorFit,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=predictedCO2,xText=0.35,yText=0.95)
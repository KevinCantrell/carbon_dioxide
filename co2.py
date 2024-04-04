import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def FormatSciUsingError(x,e,WithError=False,ExtraDigit=0):
  if abs(x)>=e:
      NonZeroErrorX=np.floor(np.log10(abs(e)))
      NonZeroX=np.floor(np.log10(abs(x)))
      formatCodeX="{0:."+str(int(NonZeroX-NonZeroErrorX+ExtraDigit))+"E}"
      formatCodeE="{0:."+str(ExtraDigit)+"E}"
  else:
      formatCodeX="{0:."+str(ExtraDigit)+"E}"
      formatCodeE="{0:."+str(ExtraDigit)+"E}"
  if WithError==True:
      return formatCodeX.format(x)+" (+/- "+formatCodeE.format(e)+")"
  else:
      return formatCodeX.format(x)

def AnnotateNLFit(fit,axisHandle,annotationText='Box',color='black',Arrow=False,xArrow='Mid',yArrow='Mid',xText=0.5,yText=0.2):
  #expected order and indexes of both coefficients and errors is as follows
  #0:initial
  #1:linear growth
  #2:second order growth
  #3:amplitude
  #4:offset
  #5:period
  c=fit['coefs']
  e=fit['errors']
  t=len(c)
  if annotationText=='Box':
      plyText=fit['labels'][0]+' + '+fit['labels'][1]+'$\cdot$day + '+fit['labels'][2]+'$\cdot$day$^2$'
      oscText=r'$\frac{'+fit['labels'][3]+r'}{2}\cdot \cos{(\frac{(day + '+fit['labels'][4]+') \cdot 2 \pi}{'+fit['labels'][5]+'})}$'
      annotationText='fit function = '+plyText+' + '+oscText+'\n'
      for order in range(t):
          annotationText=annotationText+fit['labels'][order]+" = "+FormatSciUsingError(c[order],e[order],ExtraDigit=1)+' $\pm$ '+"{0:.1E}".format(e[order])+'\n'
      annotationText=annotationText+fit['labels'][6]
      annotationText=annotationText+'n = {0:d}'.format(fit['n'])+', DoF = {0:d}'.format(fit['n']-t)+", s$_y$ = {0:.1E}".format(fit['sy'])
  if (Arrow==True):
      if (xArrow=='Mid'):
          xSpan=axisHandle.get_xlim()
          xArrow=np.mean(xSpan)
      if (yArrow=='Mid'):    
          yArrow=fit['poly'](xArrow)
      annotationObject=axisHandle.annotate(annotationText, 
              xy=(xArrow, yArrow), xycoords='data',
              xytext=(xText, yText),  textcoords='axes fraction',
              arrowprops={'color': color, 'width':1, 'headwidth':5},
              bbox={'boxstyle':'round', 'edgecolor':color,'facecolor':'0.8'}
              )
  else:
      xSpan=axisHandle.get_xlim()
      xArrow=np.mean(xSpan)
      ySpan=axisHandle.get_ylim()
      yArrow=np.mean(ySpan)
      annotationObject=axisHandle.annotate(annotationText, 
              xy=(xArrow, yArrow), xycoords='data',
              xytext=(xText, yText),  textcoords='axes fraction',
              ha="left", va="center",
              bbox={'boxstyle':'round', 'edgecolor':color,'facecolor':'0.8'}
              )
  annotationObject.draggable()
  return annotationObject

# fit={'coefs':orderedCoefs,'errors':orderedErrors,'sy':stdErrorFit,'n':len(calculatedCO2),'res':residuals,'labels':['initial','linear','exp','amplitude','offset','period','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
# annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)
# annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(predictedCO2,stdErrorFit,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=predictedCO2,xText=0.35,yText=0.95)
 
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

annotationText=str(CO2calcPrediction)
xArrow=dateToPredict
yArrow=CO2calcPrediction


annotationObject=ax.annotate(annotationText, 
        xy=(xArrow, yArrow), xycoords='data',
        xytext=(.5, .8), textcoords='axes fraction',
        arrowprops={'color': 'y', 'width':1, 'headwidth':5},
        bbox={'boxstyle':'round', 'edgecolor':'b','facecolor':'0.8'}
        )
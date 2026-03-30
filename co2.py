import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
def oscFunc(x, amp, offset, period):
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
def calcCO2(days, c2, c1, c0,amp, offset, period): 
    return days**2 *c2 + days *c1 + c0 + oscFunc(days, amp, offset, period)
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

'''reads a local file, skips 158rows, eliminate none real numbers, recalculates the index'''

dfCarbonDioxide=pd.read_table(r"co2_mlo_surface-insitu_1_ccgg_DailyData.txt",delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
''''data munging to make it usable'''
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startTime = dfCarbonDioxide['date'].min()

daysSinceStart=(dfCarbonDioxide['date']-startTime).dt.days
'''int_days = daysSinceStart.astype('timedelta64[us]').astype(int)'''
polyfit = np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)
co2 =daysSinceStart**2*polyfit[0] + polyfit[1]*daysSinceStart +polyfit[2]

ax.plot(dfCarbonDioxide['date'],co2)

co2fit = dfCarbonDioxide['value']- co2

fig2, az = plt.subplots()
az.plot(dfCarbonDioxide['date'], co2fit)

amp = 8
period = 365

yCalc = oscFunc(daysSinceStart, amp, 0, period)
az.plot(dfCarbonDioxide['date'], yCalc, color= 'red')

coefs,cov= curve_fit(calcCO2, daysSinceStart, dfCarbonDioxide['value'], p0=[polyfit[0], polyfit[1], polyfit[2], amp, 0, period])

yBestFitLine = calcCO2(daysSinceStart, coefs[0],coefs[1],coefs[2],coefs[3],coefs[4], coefs[5])

ax.plot(dfCarbonDioxide['date'],yBestFitLine, color = 'red') 


startDate = dfCarbonDioxide['date'][0]
daysFuture=np.linspace(0,int(np.ceil(365.25*60)),int(np.ceil(365.25*60)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='D')

co2InFuture = calcCO2(daysFuture,coefs[0],coefs[1],coefs[2],coefs[3],coefs[4], coefs[5])
ax.plot(datesFuture, co2InFuture)

orderedCoefs = [coefs[2], coefs[1], coefs[0], coefs[3], coefs[4], coefs[5]]
errors=np.sqrt(np.diagonal(cov))
orderedErrors = [errors[2],errors[1], errors[0], errors[3], errors[4], errors[5]]


calculatedCO2 = yBestFitLine
residuals = dfCarbonDioxide['value']-yBestFitLine
stdErrorFit = np.sqrt(np.sum(residuals**2)/(len(dfCarbonDioxide['date'])-len(coefs)))

fit={'coefs':orderedCoefs,'errors':orderedErrors,'sy':stdErrorFit,'n':len(calculatedCO2),'res':residuals,'labels':['initial','linear','exp','amplitude','offset','period','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)

dateToPredict=pd.to_datetime('2026-05-03 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
print(daysSinceStartPrediction)
predictedCO2 = calcCO2(daysSinceStartPrediction, coefs[0],coefs[1],coefs[2],coefs[3],coefs[4], coefs[5])
annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(predictedCO2,stdErrorFit,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=predictedCO2,xText=0.05,yText=0.95)
ax.set_ylabel('CO2 Levels')
ax.set_xlabel('Date')

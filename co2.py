"Imports and Functions"

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def CalcCO2Poly(days, c2, c1, c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

def CalcCO2Osc(days, amp, offset, period):  
    co2CalcOsc=amp/2 * np.cos((days + offset)  * 2 * np.pi/period)
    return co2CalcOsc

def CalcCO2PolyOsc(days, c2, c1, c0, amp, offset, period):
    co2FullCalc=CalcCO2Poly(days, c2, c1, c0)+CalcCO2Osc(days, amp, offset, period)
    return co2FullCalc

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

"-------------------------------------------------------------------------------------------------------------------------"

"Data Import and Cleaning"

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

"-------------------------------------------------------------------------------------------------------------------------"

"Conversion of Dates Into Days Since Start"

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

dateToPredict=pd.to_datetime('2027-12-31 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days

predictedDate=pd.to_datetime('2024-03-29 00:00:00')
predictedDay=(predictedDate-startDate).days

daysFuture=np.linspace(0,daysSinceStartPrediction,(daysSinceStartPrediction+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='d')

"-------------------------------------------------------------------------------------------------------------------------"

"Polyfit Functions"

fitPolyNP=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
co2fitPolyNP=CalcCO2Poly(daysSinceStart,fitPolyNP[0],fitPolyNP[1],fitPolyNP[2])

co2FitFull=CalcCO2PolyOsc(daysSinceStart,fitPolyNP[0],fitPolyNP[1],fitPolyNP[2],9,0,365)

co2OptimalFit=curve_fit(CalcCO2PolyOsc, daysSinceStart, dfCarbonDioxide['value'], p0=[fitPolyNP[0],fitPolyNP[1],fitPolyNP[2],9,0,365])
co2OptimalValues=CalcCO2PolyOsc(daysSinceStart, co2OptimalFit[0][0], co2OptimalFit[0][1], co2OptimalFit[0][2], co2OptimalFit[0][3], co2OptimalFit[0][4], co2OptimalFit[0][5])

co2PredictedValues=CalcCO2PolyOsc(daysFuture, co2OptimalFit[0][0], co2OptimalFit[0][1], co2OptimalFit[0][2], co2OptimalFit[0][3], co2OptimalFit[0][4], co2OptimalFit[0][5])
co2PredictedDay=CalcCO2PolyOsc(predictedDay, co2OptimalFit[0][0], co2OptimalFit[0][1], co2OptimalFit[0][2], co2OptimalFit[0][3], co2OptimalFit[0][4], co2OptimalFit[0][5])

res2=(dfCarbonDioxide['value']-co2OptimalValues)**2
stdErrorFit=np.sqrt((np.sum(res2))/(np.max(daysSinceStart)-6))

errorValue=FormatSciUsingError(co2PredictedDay, stdErrorFit, WithError=True, ExtraDigit=2)

"-------------------------------------------------------------------------------------------------------------------------"

"Plotting Code"

bbox = dict(boxstyle="round", fc="0.8")
arrowprops = dict(arrowstyle="->")

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
# ax.plot(dfCarbonDioxide['date'],co2fitPolyNP,'-r')
# ax.plot(dfCarbonDioxide['date'],co2FitFull,'-g')
ax.plot(datesFuture,co2PredictedValues,'-c')
# ax.plot(dfCarbonDioxide['date'],co2OptimalValues,'-r')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.annotate('Predicted $CO_{2}$ on 03-29-2024 is ' +errorValue +' ppm', (predictedDate,co2PredictedDay), (0.33,0.9),textcoords='axes fraction', bbox=bbox, arrowprops=arrowprops)

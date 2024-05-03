import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit


def CO2func(xdata,c2,c1,c0):
    concCO2=(c2*xdata**2)+(c1*xdata)+c0
    return concCO2


   
def oscFunc(xdata, amp, offset, period):  
    return amp/2 * np.cos((xdata + offset)*2*np.pi/period)
def CO2All(xdata,c2,c1,c0,amp,offset,period):
    return CO2func(xdata,c2,c1,c0)+oscFunc(xdata,amp,offset,period)

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

popt, pcov=curve_fit(CO2func,xdata,dfCarbonDioxide['value'])
c2=popt[0]
c1=popt[1]
c0=popt[2]

concCO2=CO2func(xdata,c2,c1,c0)


figr,axr=plt.subplots()
axr.plot(xdata,dfCarbonDioxide['value']-concCO2)

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

concCO2osc=CO2All(xdata,c2,c1,c0,amp,offset,period)
ax.plot(dfCarbonDioxide['date'],concCO2osc,"-r")

dateToPredict=pd.to_datetime('2024-05-05 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
print(daysSinceStartPrediction)

daysFuture=np.linspace(0,int(np.ceil(365.25*50)),int(np.ceil(365.25*50)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='d')


predictedCO2whole=CO2All(daysFuture,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])
ax.plot(datesFuture,predictedCO2whole,"-r")
predictedCO2=CO2All(daysSinceStartPrediction,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])#AnnotateNLFit(concCO2osc,ax,annotationText='Box',,color='black',Arrow=False,xArrow='Mid',yArrow='Mid',xText=0.5,yText=0.2):
orderedCoefs=[c0,c1,c2,amp,offset,period]
orderedErrors=[c0e,c1e,c2e,ampe,offsete,periode]
stdErrorFit=np.sqrt(np.sum((concCO2osc-dfCarbonDioxide['value'])**2)/(len(concCO2osc)-len(popt2)))
residuals=(concCO2osc-dfCarbonDioxide['value'])

fit={'coefs':orderedCoefs,'errors':orderedErrors,'sy':stdErrorFit,'n':len(concCO2osc),'res':residuals,'labels':['initial','linear','exp','amplitude','offset','period','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)
annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(predictedCO2,stdErrorFit,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=predictedCO2,xText=0.35,yText=0.95)

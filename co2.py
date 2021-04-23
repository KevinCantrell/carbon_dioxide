import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y
def fitOsc(x,amp,period,offset):
    #y=amp/2*np.cos(period*(x+offset))
    y=amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
    return y
    
def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x, c2, c1, c0)+fitOsc(x,amp,period,offset)
    return y


#reads file and stores it as pd dataframe
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
#converts date and time data into datetime format
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#boolean filter for missing data
boolMissing=dfCarbonDioxide['value']==-999.99
#makes missing data non values
dfCarbonDioxide[boolMissing]=np.nan
#elliminates missing data
dfCarbonDioxide=dfCarbonDioxide.dropna()
#elliminates rows that had missing data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#makes plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

dateToPredict=pd.to_datetime('2021-04-08 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPredict=dayToPredict.days
futureArray=np.arange(0,18000,1)
futureDate=pd.to_timedelta(futureArray,unit='d')+startDate
#daysSinceStartPredict=dayToPredict.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
#popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
errorsOpt=np.sqrt(np.diagonal(pcov))
#fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
#fitCO2ply=fitAll(daysSinceStart,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
fitCO2ply=fitAll(daysSinceStart,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
fitCO2Future=fitAll(futureArray,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
fitCO2OneYear=fitAll(daysSinceStartPredict,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
#ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
#ax.plot(dfCarbonDioxide['date'],fitCO2ply,'-r')
ax.plot(futureDate,fitCO2Future,'-r')
ax.plot(dateToPredict,fitCO2OneYear,'og')
#oscillationCalc=fitOsc(daysSinceStart,8,365.25,200)

#residuals=fitCO2-dfCarbonDioxide['value']
residuals=fitCO2ply-dfCarbonDioxide['value']
figRes, axRes = plt.subplots(figsize=(12,8))
#axRes.plot(dfCarbonDioxide['date'],residuals,'-b')
axRes.plot(daysSinceStart,residuals,'-b')
#axRes.plot(daysSinceStart,oscillationCalc,'-r')
oscillationCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,oscillationCalc,'y')
        
stdErrorFit=np.sqrt(np.sum(residuals**2)/(len(residuals)-len(fitCoeffs)))



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
  c=fit['coefs']
  e=fit['errors']
  t=len(c)
  if annotationText=='Box':
      oscText=r'$\frac{'+fit['labels'][3]+r'}{2}\cdot \cos{(\frac{(day + '+fit['labels'][5]+') \cdot 2 \pi}{'+fit['labels'][4]+'})}$'
      plyText=fit['labels'][2]+' + '+fit['labels'][1]+'$\cdot$day + '+fit['labels'][0]+'$\cdot$day$^2$'
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

fit={'coefs':popt,'errors':errorsOpt,'sy':stdErrorFit,'n':len(fitCO2ply),'res':residuals,'labels':['exp','linear','initial','amplitude','period','offset','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)
annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(fitCO2OneYear,stdErrorFit,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=fitCO2OneYear,xText=0.35,yText=0.95)

ax.set_ylabel(r'$CO_{2}\/(ppm)$')
ax.set_xlabel('Year')


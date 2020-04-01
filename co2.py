import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from ftplib import FTP

def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def plyFunc(x, c0, c1, c2):
    return c0+c1*x+c2*x**2

def fitFunc(x, amp, period, offset, c0, c1, c2):
    return plyFunc(x, c0, c1, c2) + oscFunc (x, amp, period, offset)

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

def AnnotateFit(fit,axisHandle,annotationText='Eq',color='black',Arrow=False,xArrow='Middle',yArrow=0,xText=0.5,yText=0.2):    
  if annotationText=='Eq':
      annotationText="[$CO_2$] = "+FormatSciUsingError(poptt[3],errors[0],WithError=False)+'+ '+FormatSciUsingError(poptt[4],errors[0],WithError=False)+"x + " +FormatSciUsingError(poptt[5],errors[0],WithError=False)+"x$^{2}$ + "+r'($\frac{5.91}{2}$)'+"*  "+r'$\mathrm{cos}$((x+'+FormatSciUsingError(poptt[2],errors[0],WithError=False)+r')*$\frac{2\pi}{365.08}$)'+'\n'
      annotationText=annotationText+"where x is the datetime"
  elif annotationText=='Box':
      annotationText="Fit Details:\n"
      annotationText=annotationText+"C$_0$ = "+FormatSciUsingError(poptt[3],errors[0],WithError=False)+", C$_1$ = "+FormatSciUsingError(poptt[4],errors[0],WithError=False)+", C$_2$ = "+FormatSciUsingError(poptt[5],errors[0],WithError=False)+'\n'
      annotationText=annotationText+"amp = "+FormatSciUsingError(poptt[0],errors[0],WithError=False)+", period = "+FormatSciUsingError(poptt[1],errors[0],WithError=False)+", offset = "+FormatSciUsingError(poptt[2],errors[0],WithError=False)+'\n'
      annotationText=annotationText+"syFIT = "+FormatSciUsingError(syerror, errors[0],WithError=False)+' ppm' +'\n'
      annotationText=annotationText+"syerrorAMP="+FormatSciUsingError(errorAMP,errors[0],WithError=False)+", syerrorPERIOD=" +FormatSciUsingError(errorPERIOD,errors[0],WithError=False)+", syerrorOFFSET=" +FormatSciUsingError(errorOFFSET,errors[0],WithError=False)+ '\n'
      annotationText=annotationText+"syerrorC$_0$="+FormatSciUsingError(errorC0,errors[0],WithError=False)+", syerrorC$_1$ =" +FormatSciUsingError(errorC1,errors[0],WithError=False)+", syerrorC$_2$ =" +FormatSciUsingError(errorC2,errors[0],WithError=False)+ '\n'
      annotationText=annotationText+"syerror Validation Set = "+FormatSciUsingError(syerrorValid, errors[0],WithError=False)+ 'ppm' 
     
  if (Arrow==True):
      if (xArrow=='Middle'):
          xSpan=axisHandle.get_xlim()
          xArrow=np.mean(xSpan)
      if (yArrow==0):    
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



ftp = FTP('ftp.cmdl.noaa.gov') 
ftp.login()
ftp.cwd('/data/trace_gases/co2/in-situ/surface/mlo/')
filename = 'co2_mlo_surface-insitu_1_ccgg_DailyData.txt'
localfile = open(filename, 'wb')
ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
ftp.quit()
localfile.close()


dfCarbonDioxide=pd.read_table(filename,delimiter=r"\s+",skiprows=146)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
dateToGrad = pd.to_datetime(['05-03-2020 00:00'])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daystoGrad = dateToGrad-startDate
daysSinceStart=timeElapsed.dt.days
daysToGrad = daystoGrad.max()

coeffs = np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)
predicted = plyFunc(daysSinceStart, coeffs[2], coeffs[1], coeffs[0])
Residual = dfCarbonDioxide['value'] - predicted

periodHolder = 365.25
amplitude = Residual.max() - Residual.min()
offset = Residual[0]-0

oscillation = oscFunc(daysSinceStart, amplitude, periodHolder, offset)

predictedValues = fitFunc (daysSinceStart, amplitude, periodHolder, offset, coeffs[2], coeffs[1], coeffs[0])

popt, pcov =curve_fit(fitFunc, daysSinceStart, dfCarbonDioxide['value'], p0=[amplitude, periodHolder, offset, coeffs[2], coeffs[1], coeffs[0]])

predictions = fitFunc (daysSinceStart, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
errors=np.sqrt(np.diag(pcov))
errorAmp=errors[0]
errorPeriod=errors[1]
errorOffset=errors[2]
errorC0=errors[3]
errorC1=errors[4]
errorC2=errors[5]  




fig, axPred = plt.subplots()
axPred.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'], 'bo')
axPred.plot(dfCarbonDioxide['date'],predictions,'ok')
axPred.set_ylabel('Carbon Dioxide')
axPred.set_xlabel('Date')

fig, axRes = plt.subplots()
Res = predictions - dfCarbonDioxide['value']
axRes.plot(dfCarbonDioxide['date'],Res,'ok')

Sum1 = np.sum(Res**2)
Sum2 = Sum1/(daysSinceStart.max()-2)
SE = np.sqrt(Sum2)

daysFuture = np.linspace(1,np.max(daysSinceStart) + 365*2,np.max(daysSinceStart) + 365*2)

days = pd.to_timedelta(daysFuture, unit='d')

pred2 = days + startDate



predExt = fitFunc (daysFuture, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
fig, axPredExt = plt.subplots()
axPredExt.set_ylabel('Carbon Dioxide')
axPredExt.set_xlabel('Date')
axPredExt.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'], 'bo')
axPredExt.plot(pred2,predExt, '-', color = 'red')


dateMay3=daysFuture[16788]
predictedMay3=fitFunc(dateMay3,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
errorMay3=np.sqrt(np.diag(pcov))
ErrorMay3 = errorMay3[0]

annGrad=AnnotateFit(predExt,axPredExt,annotationText=r'Concentration of $CO_2$ (ppm) on 05-03-2020 = '+FormatSciUsingError(predictedMay3,ErrorMay3,ExtraDigit=0)+' ppm',Arrow=True,xArrow=daysFuture[16788],yArrow=predictedMay3,xText=0.35,yText=0.95)

#annGrad=AnnotateNLFit(predExt,axPredExt,color='purple',annotationText=r'Predicted CO$_2$ on '+" is "+FormatSciUsingError(415,2,ExtraDigit=0)+" ppm",Arrow=True,xArrow=16788,yArrow=415,xText=0.35,yText=0.95)


boolDate = daysSinceStart < np.max(daysSinceStart-365)

popt1, pcov1 =curve_fit(fitFunc, daysSinceStart[boolDate], dfCarbonDioxide['value'][boolDate], p0=[amplitude, periodHolder, offset, coeffs[2], coeffs[1], coeffs[0]])

predictions2018 = fitFunc (daysSinceStart, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5]) 

fig, axPred2018 = plt.subplots()
axPred2018.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'], 'bo')
axPred2018.plot(dfCarbonDioxide['date'], predictions2018, 'ok')

bool2018 = daysSinceStart > np.max(daysSinceStart-365)

Res2018 = predictions2018[bool2018] - dfCarbonDioxide['value'][bool2018]
Sum12018 = np.sum(Res2018**2)
Sum22018 = Sum12018/(len(daysSinceStart[bool2018])-2)
SE2018 = np.sqrt(Sum22018)




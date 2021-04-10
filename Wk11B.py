import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

def fitOsc(x,amp,period,offset):
    y=amp/2*np.cos((x+offset)*2*np.pi/period)
    return y

def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y                

def AnnotateFit(fit,axisHandle,annotationText='Eq',color='black',Arrow=False,xArrow='Mid',yArrow='Mid',xText=0.5,yText=0.2):
  """
  Annotate a figure with information about a PolyReg() fit
  
  see https://matplotlib.org/api/_as_gen/matplotlib.pyplot.annotate.html
  https://matplotlib.org/examples/pylab_examples/annotation_demo3.html
  
  Parameters
  ----------
      fit: dict, returned by the function PolyReg(X,Y,order)
          the fit to be summarized in the figure annotation 
      axisHandle: a matplotlib axes class
          the axis handle to the figure to be annotated
      annotationText: string, optional
          When "Eq" (the default) displays a formatted polynomial with the coefficients (rounded according to their error) in the fit. When "Box" displays a formatted box with the coefficients and their error terms.  When any other string displays a text box with that string.
      color: a valid color specification in matplotlib, optional
          The color of the box outline and connecting arrow.  Default is black. See https://matplotlib.org/users/colors.html
      arrow: bool, optional
          If True (default=False) draws a connecting arrow from the annotation to a point on the graph.
      xArrow: float, optional 
          The X coordinate of the arrow head using units of the figure's X-axis data. If unspecified or 0 (and arrow=True), defaults to the center of the X-axis.
      yArrow: float, optional 
          The Y coordinate of the arrow head using units of the figure's Y-axis data. If unspecified or 0 (and arrow=True), defaults to the calculated Y-value at the center of the X-axis.
      xText: float, optional 
          The X coordinate of the annotation text using the fraction of the X-axis (0=left,1=right). If unspecified, defults to the center of the X-axis.
      yText: float, optional 
          The Y coordinate of the annotation text using the fraction of the Y-axis (0=bottom,1=top). If unspecified, defults to 20% above the bottom.
  
  Returns
  -------
  a dragable matplotlib Annotation class
  
  Examples
  --------
  >>> annLinear=AnnotateFit(fitLinear,ax)
  >>> annLinear.remove()
  """
  c=fit['coefs']
  e=fit['errors']
  t=len(c)
  if annotationText=='Eq':
      annotationText="y = "
      for order in range(t):
          exponent=t-order-1
          if exponent>=2:
              annotationText=annotationText+FormatSciUsingError(c[order],e[order])+"x$^{}$".format(exponent)+" + "
          elif exponent==1:
              annotationText=annotationText+FormatSciUsingError(c[order],e[order])+"x + "
          else:
              annotationText=annotationText+FormatSciUsingError(c[order],e[order])
      annotationText=annotationText+", sy={0:.1E}".format(fit['sy'])
  elif annotationText=='Box':
      annotationText="Fit Details:\n"
      for order in range(t):
          exponent=t-order-1
          annotationText=annotationText+"C$_{x^{"+str(exponent)+"}}$ = "+FormatSciUsingError(c[order],e[order],ExtraDigit=1)+' $\pm$ '+"{0:.1E}".format(e[order])+'\n'
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
  """
  Format the value, x, as a string using scientific notation and rounding appropriately based on the absolute error, e
  
  Parameters
  ----------
      x: number
          the value to be formatted 
      e: number
          the absolute error of the value
      withError: bool, optional
          When False (the default) returns a string with only the value. When True returns a string containing the value and the error
      extraDigit: int, optional
          number of extra digits to return in both value and error
  
  Returns
  -------
  a string
  
  Examples
  --------
  >>> FormatSciUsingError(3.141592653589793,0.02718281828459045)
  '3.14E+00'
  >>> FormatSciUsingError(3.141592653589793,0.002718281828459045)
  '3.142E+00'
  >>> FormatSciUsingError(3.141592653589793,0.002718281828459045,withError=True)
  '3.142E+00 (+/- 3E-03)'
  >>> FormatSciUsingError(3.141592653589793,0.002718281828459045,withError=True,extraDigit=1)
  '3.1416E+00 (+/- 2.7E-03)'
  >>> FormatSciUsingError(123456,123,withError=True)
  '1.235E+05 (+/- 1E+02)'
  """
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

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#creating figure
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days


fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
#popt,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'])
poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
#fitCO2=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
fitCO2=fitAll(daysSinceStart,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')
        
res=fitCO2-dfCarbonDioxide['value']
figRes,axRes=plt.subplots()
axRes.plot(daysSinceStart,res)

stdErr=np.sqrt(np.sum(res**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))

oscCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,oscCalc)

#predicting levels in May
dateToPredict=pd.to_datetime('2021-04-08 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
predictedCO2=fitAll(daysSinceStartPrediction,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(dateToPredict,predictedCO2,'og')
print(daysSinceStartPrediction)


#predicts years in the future
daysFuture=np.linspace(0,int(np.ceil(365.25*50)),int(np.ceil(365.25*50)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture,unit='d') 
futureCO2=fitAll(daysFuture,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(datesFuture,futureCO2,'-r')

AnnotateFit(dateToPredict,ax,color='xkcd:dark purple',annotationText=r'Predicted CO2 on April-08-2021 is = '+FormatSciUsingError(predictedCO2,0.1,ExtraDigit=1),Arrow=True,xArrow=0, xText=0.3,yText=0.1)





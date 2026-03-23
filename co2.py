import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
 
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

def PolyReg(X,Y,order=1):
  """
  Perform a least squares polynomial fit

  Parameters
  ----------
      X: a numpy array with shape M
          the independent variable
      Y: a numpy array with shape M
          the dependent variable
      order: integer
          the degree of the fitting polynomial

  Returns
  -------{0:1.5f}'.format(3.141592)
  a dict with the following keys:
      'coefs': a numpy array with length order+1
          the coefficients of the fitting polynomial, higest order term first
      'errors': a numpy array with length order+1
          the standard errors of the calculated coefficients,
          only returned if (M-order)>2
      'sy': float
          the standard error of the fit
      'n': integer
          number of data points (M)
      'poly':  class in numpy.lib.polynomial module
          a polynomial with coefficients (coefs) and degreee (order),
          see example below
      'res': a numpy array with length M
          the residuals of the fit

  Examples
  --------
  >>> x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
  >>> y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
  >>> fit = PolyReg(x, y, 2)
  >>> fit
  {'coefs': array([-0.16071429,  0.50071429,  0.22142857]),
    'errors': array([0.06882765, 0.35852091, 0.38115025]),
    'n': 6,
    'poly': poly1d([-0.16071429,  0.50071429,  0.22142857]),
    'res': array([-0.22142857,  0.23857143,  0.32      , -0.17714286, -0.45285714,
        0.29285714]),
    'sy': 0.4205438655564278}

  It is convenient to use the "poly" key for dealing with fit polynomials:

  >>> fit['poly'](0.5)
  0.43160714285714374
  >>> fit['poly'](10)
  -10.842857142857126
  >>> fit['poly'](np.linspace(0,10,11))
  array([  0.22142857,   0.56142857,   0.58      ,   0.27714286,
      -0.34714286,  -1.29285714,  -2.56      ,  -4.14857143,
      -6.05857143,  -8.29      , -10.84285714])
  """
  n=len(X)
  df=n-(order+1)
  if df==0:
    coefs=np.polyfit(X,Y,order)
    errors=np.zeros(coefs.shape)
  else:
    coefs,cov=np.polyfit(X,Y,order,cov=True)
    errors=np.sqrt(np.diagonal(cov))
  poly=np.poly1d(coefs)
  Yfit=poly(X)
  res=Y-Yfit
  if df==0:
    sy=0
  else:
    sy=np.sqrt( np.sum(res**2) / df )
  return {'coefs':coefs,'errors':errors,'sy':sy,'n':n,'poly':poly,'res':res}

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
          annotationText=annotationText+"C$_{x^{"+str(exponent)+"}}$ = "+FormatSciUsingError(c[order],e[order],ExtraDigit=1)+r' $\pm$ '+"{0:.1E}".format(e[order])+'\n'
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

import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"
#pio.renderers.default = "colab"

#read local file, set the delimiter or where information if separated as a space, skip the first 158 header lines.
dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158)
#create a new coloumn called 'date' using the year month day hour minute and second coloumns. 
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
#search the data for any entries that have a value of -999.99 which represents no data collection for that day. 
boolMissing=dfCarbonDioxide['value']==-999.99
#set these entries as the pandas definition of not a real number or 'nan'
dfCarbonDioxide[boolMissing]=np.nan
#remove these rows of data from the table and shuffle the index order to be correct for the new table excluding these missing entries
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startTime=dfCarbonDioxide['date'].min()
daysSinceStart=(dfCarbonDioxide['date']-startTime).dt.days

PolyFit=np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2, rcond=None, full=False, w=None, cov=False)
CO2Fit=(daysSinceStart**2*PolyFit[0]+PolyFit[1]*daysSinceStart+PolyFit[2])
ax.plot(dfCarbonDioxide['date'], CO2Fit, '-r')

ResidualY=dfCarbonDioxide['value']-CO2Fit

fig,ax2=plt.subplots()
ax2.plot(daysSinceStart,ResidualY)

def oscFunc(x, amp, offset, period):
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period)

x = daysSinceStart.values
y = ResidualY.values

# initial guesses help convergence
guess = [2.0, 0.0, 365]

params = curve_fit(oscFunc, x, y, p0=guess)

A, phi, offset = params[0]
print("Amplitude:", A)
print("Phase:", phi)
print("Offset:", offset)

season_fit = oscFunc(x, A, phi, offset)

fig, ax3 = plt.subplots()
ax3.plot(x, y, '.', label='Residuals')
ax3.plot(x, season_fit, 'r-', label='Cosine Fit')

FullModel = CO2Fit + season_fit

fig,ax3 = plt.subplots(figsize=(12,8))

# original data
ax3.plot(dfCarbonDioxide['date'], dfCarbonDioxide['value'], '.k', label='Data')

# polynomial trend only
ax3.plot(dfCarbonDioxide['date'], CO2Fit, 'r--', label='Trend (Polynomial)')

# full model (trend + seasonal)
ax3.plot(dfCarbonDioxide['date'], FullModel, 'b-', label='Trend + Seasonal')

ax3.set_xlabel("Date")
ax3.set_ylabel("CO2 Concentration (ppm)")
ax3.legend()

plt.show()

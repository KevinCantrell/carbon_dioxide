import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

def PolyReg(x,y,order=1): #for A-Level revisit order
    n=len(x)
    df=n-(1+order) #number of data points minus the order plus 1
    coefs,cov=np.polyfit(x,y,order,cov=True)
    errors=np.sqrt(np.diagonal(cov))
    poly=np.poly1d(coefs)
    yFit=poly(x)
    res=yFit-y
    sy=np.sqrt(sum(res**2)/df)
    return{'coefs':coefs,'errors':errors,'sy':sy,'n':n,'poly':poly,'res':res,'df':df, 'yFit':yFit, 'slope':coefs[-2], 'intercept':coefs[-1], 'errM':errors[-2], 'errB':errors[-1]}

def CO2Func(days,C0,C1,C2,amp,off,per):
    return C2*days**2+C1*days+C0+amp/2*np.cos(((days+off)*2*np.pi)/per)

def CO2Conc(day,C2,C1,C0,amp,off,per):
    CO2=C2*day**2+C1*day+C0+amp/2*np.cos(((day+off)*2*np.pi)/per)
    return CO2                            
            
#def AnnotateNLFit(fit,axisHandle,annotationText='Box',color='black',Arrow=False,xArrow='Mid',yArrow='Mid',xText=0.5,yText=0.2):
  #expected order and indexes of both coefficients and errors is as follows
  #0:initial
  #1:linear growth
  #2:second order growth
  #3:amplitude
  #4:offset
  #5:period
#

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

dfCarbonDioxide=pd.read_table('co2_mlo_surface-insitu_1_ccgg_DailyData.txt',delimiter=r"\s+",skiprows=158) #reading the data from a txt file and letting it know what to skip and how different data is notated
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']]) #reading the date data only
boolMissing=dfCarbonDioxide['value']==-999.99 #starting to get rid of n/a data
dfCarbonDioxide[boolMissing]=np.nan #replacing data with n/a
dfCarbonDioxide=dfCarbonDioxide.dropna() #telling the script to reomve n/a data
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True) #finalizing the data

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

finalDate=pd.to_datetime('2025-05-04 00:00:00')
finalDay=finalDate-startDate
finalDayPredic=finalDay.days

fit1=PolyReg(daysSinceStart,dfCarbonDioxide['value'],order=2)
C2=fit1['coefs'][0]
C1=fit1['coefs'][1]
C0=fit1['coefs'][2]
popt,pcov=curve_fit(CO2Func,daysSinceStart,dfCarbonDioxide['value'],p0=[C2,C1,C0,10,200,365])
dayFuture=np.linspace(0,int(np.ceil(365.25*55)),int(np.ceil(365.25*55)+1))
dateFuture=startDate+pd.to_timedelta(dayFuture,unit='d')

#futureConc=CO2Conc(finalDayPredic, *popt)
#allFutureConc=CO2Conc(daysSinceStart,*popt)
#res=allFutureConc-dfCarbonDioxide['value']
#df=len(dfCarbonDioxide['date'])-len(popt)
#sy=np.sum(np.sqrt((np.sum(res**2))/df))
#concPre=FormatSciUsingError(futureConc,sy,WithError=True)



fig,ax = plt.subplots(figsize=(12,8)) #making a figure
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k') #plotting the known data as black small points
ax.format_xdata=mdates.DateFormatter('%Y-%m-%d') #formating the dates to be consitent
ax.plot(dateFuture,CO2Func(dayFuture,*popt),'r')
ax.set_ylabel('$CO_2$ Concentration (ppm)')
ax.set_xlabel('Date')
#predictBox=AnnotateNLFit(popt,ax,annotationText='Predicted $CO_2$ on May-04-2025 is '+str(concPre)+'ppm',Arrow=True,xText=.95,yText=.35,xArrow=finalDate,yArrow=futureConc)
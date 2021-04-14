import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from ftplib import FTP

#domain name or server ip:
ftp = FTP('aftp.cmdl.noaa.gov')
ftp.login() 
ftp.cwd('data/trace_gases/co2/in-situ/surface/mlo/')
filename = 'co2_mlo_surface-insitu_1_ccgg_DailyData.txt'

localfile = open('co2_mlo.txt', 'wb')
ftp.retrbinary('RETR ' + filename, localfile.write, 1024)

ftp.quit()
localfile.close()

def fitPly(x,c2,c1,c0):
    y=x**2*c2+x*c1+c0
    return y

#def fitPly3(x,c3,c2,c1,c0):
    #y=x**3*c3+x**3*c2+x*c1+c0
    #return y

def fitOsc(x,amp,period,offset):
    y=amp/2 * np.cos((x + offset)  * 2 * np.pi/period)
    #y=amp*np.cos(period*(x+offset))
    return y

#def fitAll(x,c2,c1,c0,amp,period,offset):
    #y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
   # return y
def fitAll(x,c2,c1,c0,amp,period,offset):
    y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    return y

#def fitPart(x,c2,c1,c0,amp,period,offset):
    #y=fitPly(x,c2,c1,c0)+fitOsc(x,amp,period,offset)
    #return y

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
      oscText=r'$\frac{'+fit['labels'][0]+r'}{2}\cdot \cos{(\frac{(day + '+fit['labels'][2]+') \cdot 2 \pi}{'+fit['labels'][1]+'})}$'
      plyText=fit['labels'][3]+' + '+fit['labels'][4]+'$\cdot$day + '+fit['labels'][5]+'$\cdot$day$^2$'
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



dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)

#make a plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

fitCoeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
fitCO2=fitPly(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2])
ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

#fitCoeffs3=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],3)
#poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs3[0],fitCoeffs3[1],fitCoeffs3[2],fitCoeffs3[3],8,365.25,200])
poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=[fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200])
#poptAll,pcov=curve_fit(fitAll,daysSinceStart,dfCarbonDioxide['value'],p0=fitCoeffs3[0],fitCoeffs[1],fitCoeffs3[2],fitCoeffs3[3],8,365.25,200 )
#fitCO2Ply=fitAll(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2],8,365.25,200)
#ax.plot(dfCarbonDioxide['date'],fitCO2,'-r')

fitCO2ply=fitPly(daysSinceStart,fitCoeffs[0],fitCoeffs[1],fitCoeffs[2])
fitCO2all=fitAll(daysSinceStart,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
#fitCO2part=fitPart(daysSinceStart,poptPart[0],poptPart[1],poptPart[2],poptPart[3],poptPart[4],poptPart[5])

ax.plot(dfCarbonDioxide['date'],fitCO2all,'-r')
ax.plot(dfCarbonDioxide['date'],fitCO2ply,'-b')
#ax.plot(dfCarbonDioxide['date'],fitCO2part,'-g')

residualsAll=fitCO2all-dfCarbonDioxide['value']
#residualsPart=fitCO2part-dfCarbonDioxide['value']
residualsPly=fitCO2ply-dfCarbonDioxide['value']

figRes,axRes=plt.subplots(figsize=(12,8))
axRes.plot(daysSinceStart,residualsAll,'-r')
axRes.plot(daysSinceStart,residualsPly,'-b')
#axRes.plot(daysSinceStart,residualsPart,'-g')
#axRes.plot(dfCarbonDioxide['date'],residuals)
#stdError=np.sqrt(np.sum(residuals**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))
#pyplOscillationCalc=fitOsc(daysSinceStart,8,365.25,200)
#axRes.plot(daysSinceStart,OscillationCalc)

#rss1=np.sum(residualsPart**2)
#rss2=np.sum(residualsAll**2)
#p1=len(poptPart)
#p2=len(poptAll)
n=len(dfCarbonDioxide['value'])
#fcalc=((rss1-rss2)/(p2-p1))/(rss2/(n-p2))
#fTable=stats.f.ppf(1-(0.05),p2-p1,n-p2)

stdErrorPly=np.sqrt(np.sum(residualsPly**2)/(len(dfCarbonDioxide['value'])-len(poptAll)))
sy=np.sqrt(np.sum(residualsAll**2)/(len(dfCarbonDioxide['value'])-len(fitCoeffs)))
#stdErrorPart=np.sqrt(np.sum(residualsPart**2)/(len(dfCarbonDioxide['value'])-len(poptPart)))

dateToPredict=pd.to_datetime('2021-04-08 00:00:00')
dayToPredict=dateToPredict-startDate
daysSinceStartPrediction=dayToPredict.days
print(daysSinceStartPrediction)
predictedCO2=fitAll(daysSinceStartPrediction,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])

daysFuture=np.linspace(0,int(np.ceil(365.25*50)),int(np.ceil(365.25*50)+1))
datesFuture=startDate+pd.to_timedelta(daysFuture, unit='d')
predictedCO2F=fitAll(daysFuture,poptAll[0],poptAll[1],poptAll[2],poptAll[3],poptAll[4],poptAll[5])
ax.plot(datesFuture,predictedCO2F,'-r')
errors=np.sqrt(np.diagonal(pcov))


fit={'coefs':poptAll,'errors':errors,'sy':sy,'n':len(dfCarbonDioxide['value']),'res':residualsPly,'labels':['exp','linear','initial','amplitude','period','offset','day = days since '+startDate.strftime('%b-%d-%Y')+'\n']}
annBox=AnnotateNLFit(fit,ax,annotationText='Box',color='black',Arrow=False,xText=0.42,yText=0.14)
annPrediction=AnnotateNLFit(fit,ax,color='green',annotationText=r'Predicted CO$_2$ on '+dateToPredict.strftime('%b-%d-%Y')+" is "+FormatSciUsingError(predictedCO2,sy,ExtraDigit=1,WithError=True)+r" ppm",Arrow=True,xArrow=dateToPredict,yArrow=predictedCO2,xText=0.35,yText=0.95)
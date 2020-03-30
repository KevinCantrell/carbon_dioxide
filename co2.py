import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
import datetime


dfCarbonDioxide=pd.read_table(r'C:\Users\eng20\Desktop\CO2MLO.txt',delimiter=" ",skiprows=146)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)
print(dfCarbonDioxide)

fig, ax = plt.subplots(figsize=(12,8))   #Figure 1
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")
ax.set_title('Observed Concentration of $CO_2$ Over Time')
plt.show()

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

xdata=daysSinceStart
ydata=dfCarbonDioxide['value']

def plyFunc(x,c0,c1,c2):
    return c0+x*c1+x**2*c2


coeffs=np.polyfit(xdata,ydata,2)
fig1,(axResidual,ax2Residual,ax6Residual)=plt.subplots(3,1,figsize=(12,8),gridspec_kw={'hspace': 0.8, 'wspace':0}) #Figure 2
predicted=plyFunc(xdata,coeffs[2],coeffs[1],coeffs[0])
axResidual.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value']-predicted,'ok')
axResidual.set_xlabel("Year")
axResidual.set_ylabel("Concentration of $CO_2$ (ppm)")
axResidual.set_title('Residuals of Polynomial Fit')
print(coeffs[0:])

def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def newFunc(x,amp, period, offset,c0,c1,c2):
    return plyFunc(x,c0,c1,c2)+oscFunc(x, amp, period, offset)
    

amp=8
period=365.25 #days
offset=0

#fig2,ax2Residual=plt.subplots() #Figure 3
predicted2=oscFunc(xdata,amp,period,offset)
ax2Residual.plot(dfCarbonDioxide['date'],predicted-predicted2,'ok')
ax2Residual.set_xlabel("Year")
ax2Residual.set_ylabel("Concentration of $CO_2$ (ppm)")
ax2Residual.set_title('Residuals of Oscillation Wave Fit')


poptt,pcov=curve_fit(newFunc,xdata,dfCarbonDioxide['value'],p0=[amp, period, offset,coeffs[0],coeffs[1],coeffs[2]])
#pcov is covariance 


print('amplitude',poptt[0]) #amp
print('period',poptt[1]) #period
print('offset',poptt[2]) #offset

print('C0',poptt[3]) #coeffs2
print('C1',poptt[4]) #coeffs1
print('C2',poptt[5]) #coeffs0

errors=np.sqrt(np.diag(pcov))

#standard errors for each fitting coef
errorAMP=errors[0]

errorPERIOD=errors[1]

errorOFFSET=errors[2]

errorC0=errors[3]

errorC1=errors[4]

errorC2=errors[5]          

print('errorAMP',errorAMP) #amp
print('errorPERIOD',errorPERIOD) #period
print('errorOFFSET',errorOFFSET) #offset

print('errorC0',errorC0) #coeffs2
print('errorC1',errorC1) #coeffs1
print('errorC2',errorC2) #coeffs0


Co2predicted1=newFunc(xdata,poptt[0],poptt[1],poptt[2],poptt[3],poptt[4],poptt[5])


#plot daysSinceStart and not Date

daystoCalc=np.linspace(0,16299+365*2,(16299+(365*2)-1))
Co2predicted=newFunc(daystoCalc,poptt[0],poptt[1],poptt[2],poptt[3],poptt[4],poptt[5])
#ax.plot(daysSinceStart,Co2predicted,'yellow')


#fig3,CO2PredictedFx=plt.subplots()
#CO2PredictedFx.plot(daystoCalc,Co2predicted,'yellow')


fig4,ax4comparison=plt.subplots(figsize=(12,8))
ax4comparison.plot(daysSinceStart,dfCarbonDioxide['value'],'ok')
ax4comparison.plot(daystoCalc,Co2predicted,'yellow')
ax4comparison.set_xlabel("Number of Days Since May 17, 1974")
ax4comparison.set_ylabel("Concentration of $CO_2$ insitu at Mauna Loa (ppm)")
ax4comparison.set_title('Determination of the Concentration of $CO_2$ at Mauna Loa Throughout Time')

errors=np.sqrt(np.diag(pcov))
Co2concerror=errors[0]

#overallfunc=c0+c1x+c2x^2+amp/2*cos(x+offset)*(2pi/period)

DateofMay3rd=daystoCalc[16787]
Co2concMay3rd=newFunc(DateofMay3rd,poptt[0],poptt[1],poptt[2],poptt[3],poptt[4],poptt[5])
print ("Predicted [CO2] on May 3, 2020:","{:.2f}".format(Co2concMay3rd))

#ESTIMATE ERROR:

#fig6,ax6Residual=plt.subplots()
ax6Residual.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value']-Co2predicted1,'ok')
ax6Residual.set_xlabel("Year")
ax6Residual.set_ylabel("Concentration of $CO_2$ (ppm)")
ax6Residual.set_title('Residuals of Optimized Curve Fit')




df=len(Co2predicted1)-6 #6 coefficients
STresidual=dfCarbonDioxide['value']-Co2predicted1
syerror=np.sqrt(np.sum(STresidual**2)/df)
print('Standard-error(sy)=',syerror)



def AnnotateFit(fit,axisHandle,annotationText='Eq',color='black',Arrow=False,xArrow='Middle',yArrow=0,xText=0.5,yText=0.2):    
  #c=fit['coefs']
  #e=fit['errors']
  #t=len(c)
  if annotationText=='Eq':
      #annotationText="[$CO_2$] = "+FormatSciUsingError(poptt[3],errors[0],WithError=False)+'+ '+FormatSciUsingError(poptt[4],errors[0],WithError=False)+"x + " +FormatSciUsingError(poptt[5],errors[0],WithError=False)+"x$^{2}$ + "+FormatSciUsingError(poptt[0],errorAMP,WithError=False)+"*  "+r'$\mathrm{cos}$((x+'+FormatSciUsingError(poptt[2],errors[0],WithError=False)+r')*$\frac{2\pi}{365.08}$)'+'\n'
      annotationText="[$CO_2$] = "+FormatSciUsingError(poptt[3],errors[0],WithError=False)+'+ '+FormatSciUsingError(poptt[4],errors[0],WithError=False)+"x + " +FormatSciUsingError(poptt[5],errors[0],WithError=False)+"x$^{2}$ + "+r'($\frac{5.91}{2}$)'+"*  "+r'$\mathrm{cos}$((x+'+FormatSciUsingError(poptt[2],errors[0],WithError=False)+r')*$\frac{2\pi}{365.08}$)'+'\n'
      annotationText=annotationText+"where x is the datetime"
      #annotationText=annotationText+", sy={0:.1E}".format(fit['sy'])
  elif annotationText=='Box':
      annotationText="Fit Details:\n"
      annotationText=annotationText+"C$_0$ = "+FormatSciUsingError(poptt[3],errors[0],WithError=False)+", C$_1$ = "+FormatSciUsingError(poptt[4],errors[0],WithError=False)+", C$_2$ = "+FormatSciUsingError(poptt[5],errors[0],WithError=False)+'\n'
      annotationText=annotationText+"amp = "+FormatSciUsingError(poptt[0],errors[0],WithError=False)+", period = "+FormatSciUsingError(poptt[1],errors[0],WithError=False)+", offset = "+FormatSciUsingError(poptt[2],errors[0],WithError=False)+'\n'
      annotationText=annotationText+"syFIT = "+FormatSciUsingError(syerror, errors[0],WithError=False)+' ppm' +'\n'
      annotationText=annotationText+"syerrorAMP="+FormatSciUsingError(errorAMP,errors[0],WithError=False)+", syerrorPERIOD=" +FormatSciUsingError(errorPERIOD,errors[0],WithError=False)+", syerrorOFFSET=" +FormatSciUsingError(errorOFFSET,errors[0],WithError=False)+ '\n'
      annotationText=annotationText+"syerrorC$_0$="+FormatSciUsingError(errorC0,errors[0],WithError=False)+", syerrorC$_1$ =" +FormatSciUsingError(errorC1,errors[0],WithError=False)+", syerrorC$_2$ =" +FormatSciUsingError(errorC2,errors[0],WithError=False)+ '\n'
      #annotationText=annotationText+'n = {0:d}'.format(fit['n'])+', DoF = {0:d}'.format(fit['n']-t)+", s$_y$ = {0:.1E}".format(fit['sy'])
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



addon=pd.to_timedelta(daystoCalc, unit='d')
newxaxis=startDate+addon



#validationset
validdataX=dfCarbonDioxide['date'][13281:]
validdataY=dfCarbonDioxide['value'][13281:]
newxaxis[15934] #Jan 1 2018
validdataYfit=Co2predicted1[13281:]
validresiduals=(validdataYfit-validdataY)
df=len(validdataY)-6
syerrorValid=np.sqrt(np.sum(validresiduals**2)/df)
print('Standard-error 2018 data=',syerrorValid)


#validationplotfit
#fig8,ax8valid=plt.subplots(figsize=(12,8))
#ax8valid.plot(dfCarbonDioxide['date'][:13281],dfCarbonDioxide['value'][:13281],'ok')
#ax8valid.plot(dfCarbonDioxide['date'][:13281],Co2predicted1[:13281],'pink')
#ax8valid.set_xlabel("Year")
#ax8valid.set_ylabel("Concentration of $CO_2$ insitu at Mauna Loa (ppm)")
#ax8valid.set_title('(ValidationFit)Determination of the Concentration of $CO_2$ at Mauna Loa From 1974-2017')



fig7,ax7final=plt.subplots(figsize=(12,8))
ax7final.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax7final.plot(newxaxis,Co2predicted,'yellow')
ax7final.set_xlabel("Year")
ax7final.set_ylabel("Concentration of $CO_2$ insitu at Mauna Loa (ppm)")
ax7final.set_title('Determination of the Concentration of $CO_2$ at Mauna Loa Throughout Time')

ann1=AnnotateFit(Co2predicted,ax7final,annotationText='Box',color='yellow',xText=0.025,yText=0.85)

ann2=AnnotateFit(Co2predicted,ax7final,annotationText='Concentration of $CO_2$ (ppm) on 5/3/2020 = '+FormatSciUsingError(Co2concMay3rd,Co2concerror,WithError=False,ExtraDigit=0)+' ppm',color='orange',Arrow=True,xArrow=newxaxis[16787],yArrow=Co2concMay3rd,xText=0.5,yText=0.2)

ann3=AnnotateFit(Co2predicted,ax7final,annotationText='Eq',color='yellow',xText=0.025,yText=0.65)

with pd.ExcelWriter(r'C:\Users\eng20\Desktop\CO2MLORaw.xlsx') as writer:
    dfCarbonDioxide.to_excel(writer, sheet_name='RawData')


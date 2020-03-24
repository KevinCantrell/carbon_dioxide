import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit

def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def plyFunc(x, c0, c1, c2):
    return c0+c1*x+c2*x**2

def fitFunc(x, amp, period, offset, c0, c1, c2):
    return plyFunc(x, c0, c1, c2) + oscFunc (x, amp, period, offset)

dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=146)
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
boolMissing=dfCarbonDioxide['value']==-999.99
dfCarbonDioxide[boolMissing]=np.nan
dfCarbonDioxide=dfCarbonDioxide.dropna()
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)
print(dfCarbonDioxide)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days
#x variable is daysSinceStart

coeffs = np.polyfit(daysSinceStart, dfCarbonDioxide['value'], 2)
predicted = plyFunc(daysSinceStart, coeffs[2], coeffs[1], coeffs[0])
Residual = dfCarbonDioxide['value'] - predicted

fig, axResidual = plt.subplots()
axResidual.plot(dfCarbonDioxide['date'],Residual,'ok')

periodHolder = 365.25
amplitude = Residual.max() - Residual.min()
offset = Residual[0]-0

oscillation = oscFunc(daysSinceStart, amplitude, periodHolder, offset)

fig, axOscillation = plt.subplots()
axOscillation.plot(dfCarbonDioxide['date'],oscillation,'ok')

predictedValues = fitFunc (daysSinceStart, amplitude, periodHolder, offset, coeffs[2], coeffs[1], coeffs[0])

fig, axPredicted = plt.subplots()
axPredicted.plot(dfCarbonDioxide['date'],predictedValues,'ok')
axPredicted.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')

secondResiduals = predictedValues - dfCarbonDioxide['value']
axResidual.plot(dfCarbonDioxide['date'],secondResiduals,'ok')

popt, pcov =curve_fit(fitFunc, daysSinceStart, dfCarbonDioxide['value'], p0=[amplitude, periodHolder, offset, coeffs[2], coeffs[1], coeffs[0]])
'''
popt[0] = amp
popt[1] = period
popt[2] = offset
'''
predictionSecond = fitFunc (daysSinceStart, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
fig, axPredictions = plt.subplots()
axPredictions.plot(dfCarbonDioxide['date'],predictionSecond,'ok')

thirdResiduals = predictionSecond - dfCarbonDioxide['value']
axResidual.plot(dfCarbonDioxide['date'],thirdResiduals,'ok')


predictionSecond2 = fitFunc (daysSinceStart, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
fig, axPredictions2 = plt.subplots()
axPredictions2.plot(dfCarbonDioxide['date'],predictionSecond2,'ok')
axPredictions2.set_ylabel('Carbon Dioxide')
axPredictions2.set_xlabel('Date')

fig, axResidual2 = plt.subplots()
secondResiduals2 = predictionSecond2 - dfCarbonDioxide['value']
axResidual2.plot(dfCarbonDioxide['date'],secondResiduals2,'ok')



"Imports and Functions"

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy import stats

<<<<<<< Updated upstream
def CalcCO2Poly(days,c2,c1,c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

=======
def CalcCO2Poly(days, c2, c1, c0):
    co2calc=c2*days**2+c1*days+c0
    return co2calc

def CalcCO2Osc(days, amp, offset, period):  
    co2CalcOsc=amp/2 * np.cos((days + offset)  * 2 * np.pi/period)
    return co2CalcOsc

def CalcCO2PolyOsc(days, c2, c1, c0, amp, offset, period):
    co2FullCalc=CalcCO2Poly(days, c2, c1, c0)+CalcCO2Osc(days, amp, offset, period)
    return co2FullCalc

>>>>>>> Stashed changes
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

"-------------------------------------------------------------------------------------------------------------------------"

"Polyfit Fucntions"

fitPolyNP=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)
co2fitPolyNP=CalcCO2Poly(daysSinceStart,fitPolyNP[0],fitPolyNP[1],fitPolyNP[2])

<<<<<<< Updated upstream
=======
res=(dfCarbonDioxide['value']-co2fitPolyNP)
resFit=CalcCO2Osc(daysSinceStart,9,0,365)

co2FitFull=CalcCO2PolyOsc(daysSinceStart,fitPolyNP[0],fitPolyNP[1],fitPolyNP[2],9,0,365)

co2OptimalFit=curve_fit(CalcCO2PolyOsc, daysSinceStart, dfCarbonDioxide['value'], p0=[fitPolyNP[0],fitPolyNP[1],fitPolyNP[2],9,0,365])
co2OptimalValues=CalcCO2PolyOsc(daysSinceStart, co2OptimalFit[0][0], co2OptimalFit[0][1], co2OptimalFit[0][2], co2OptimalFit[0][3], co2OptimalFit[0][4], co2OptimalFit[0][5])

>>>>>>> Stashed changes
"-------------------------------------------------------------------------------------------------------------------------"

"Plotting Code"

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'.k')
<<<<<<< Updated upstream
ax.plot(dfCarbonDioxide['date'],co2fitPolyNP,'-r')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')




=======
# ax.plot(dfCarbonDioxide['date'],co2fitPolyNP,'-r')
# ax.plot(dfCarbonDioxide['date'],co2FitFull,'-g')
ax.plot(dfCarbonDioxide['date'],co2OptimalValues,'-c')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

figRes, axRes = plt.subplots(figsize=(12,8))
axRes.plot(daysSinceStart,res)
axRes.plot(daysSinceStart,resFit)
>>>>>>> Stashed changes

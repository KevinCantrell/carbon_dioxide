# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:48:35 2021

@author: sk8er
"""
#Michelle Rodriguez
#CHM-477A
#Green House

#imports
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from scipy.optimize import curve_fit


register_matplotlib_converters()

#defining functions, given funtions
def oscFunc(x, amp, period, offset):  
    return amp/2 * np.cos((x + offset)  * 2 * np.pi/period) 

def plyFunc(x,c0,c1,c2):
    return c0+x*c1+x**2*c2

#reading table
dfCarbonDioxide=pd.read_table('co2_mlo.txt',delimiter=r"\s+",skiprows=151)


#removing missing data
    #missing values are given ad -999.99
boolMissing=dfCarbonDioxide['value']==-999.99
    #missing datat is replaced by nan
dfCarbonDioxide[boolMissing]=np.nan
    #remcoves data that has na values
dfCarbonDioxide=dfCarbonDioxide.dropna()
    #resets the index to account for drop
dfCarbonDioxide=dfCarbonDioxide.reset_index(drop=True)



#Changing Date, eliminating time specifics, and moving date to first column
    #makes the dates and time into a single output and lists it under data
dfCarbonDioxide['date']=pd.to_datetime(dfCarbonDioxide[['year', 'month', 'day', 'hour', 'minute', 'second']])
    #removes the colums
dfCarbonDioxide=dfCarbonDioxide.drop(columns=['year', 'month', 'day','hour', 'minute', 'second'],axis=1)
    #reorganizes colums
dfCarbonDioxide=dfCarbonDioxide[["date","site_code","time_decimal",'value', 'value_std_dev', 'nvalue', 'latitude', 'longitude', 'altitude', 'elevation', 'intake_height', 'qcflag']]

#plotting data
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value'],'ok')
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.set_xlabel("Date")
ax.set_ylabel("ppm $CO_2$ insitu at Mauna Loa")

#time elapsed calculation
startDate=min(dfCarbonDioxide['date'])
timeElapsed=dfCarbonDioxide['date']-startDate
daysSinceStart=timeElapsed.dt.days

coeffs=np.polyfit(daysSinceStart,dfCarbonDioxide['value'],2)


predicted=plyFunc(daysSinceStart,coeffs[2],coeffs[1],coeffs[0])

fig,axResidual=plt.subplots()
axResidual.plot(dfCarbonDioxide['date'],dfCarbonDioxide['value']-predicted,'ok')
# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import numpy as np
from math import sqrt
from CS_StockData import *
from CS_Graphing import *


##########################################################
# Moving Average Convergence-Divergence


def calcMACD(df,ma_fast,ma_slow,macd_period):
    '''Moving Average Convergence Divergence (MACD)'''
    #ma_fast is periods included in fast moving average
    #ma_slow is periods included in fast moving average
    #macd_period is periods included in MA of MA

    ma_fast = calcMovingAverage(df,ma_fast)
    ma_slow = calcMovingAverage(df,ma_slow)
    ma_diff = []
    macd = []

    for x in range(0,len(ma_slow)):
        ma_diff.append(ma_fast[x]-ma_slow[x])
    
    macd = calcMovingAverage(ma_diff,macd_period)

    #lists of different lengths
    return ma_diff, macd


def calcMACDForGraphs(df,ma_fast,ma_slow,macd_period):
    '''Moving Average Convergence Divergence (MACD)'''

    ma_fast = calcMovingAverage(df,ma_fast)
    ma_slow = calcMovingAverage(df,ma_slow)
    ma_diff = []
    macd = []
    length = len(df)

    for x in range(0,len(ma_slow)):
        ma_diff.append(ma_fast[x]-ma_slow[x])
    
    macd = calcMovingAverage(ma_diff,macd_period)
    
    for x in range(0,length-len(ma_diff)):
        ma_diff.append(None)
    
    for x in range(0,length-len(macd)):
        macd.append(None)

    #lists of different lengths
    return ma_diff, macd


def calcMovingAverage(df, a):
    '''General moving average function'''
    length = len(df)-a
    ma_data =[]

    for x in range(0,length):
        total = 0
        for y in range(0, a):
            total += df[x+y]
        ma_data.append(total/a)

    return ma_data


def pullMACDPoints(ma_diff,macd):
    '''Identify index position of where MACD lines cross'''
    #initiate list to capture points where lines cross
    indexMACDpoints = []

    #running prior period value to determine if new value indicates lines crossed
    prior_period = 0

    for x in range(0, len(macd)):
        
        if x == 0:
            prior_period = ma_diff[x]-macd[x]
        
        else:
            current_period = ma_diff[x]-macd[x]

            if current_period < 0 and prior_period >= 0:
                indexMACDpoints.append([x,"buy"])
                prior_period = current_period
            elif current_period > 0 and prior_period <= 0:
                indexMACDpoints.append([x,"sell"])
                prior_period = current_period
            else:
                continue
    
    return indexMACDpoints


##########################################################
# Volume-Price Trend


def calcVolPriceTrend(df):
    '''Calculates volume-price trend for stock'''
    #https://www.daytrading.com/volume-price-trend
    #used to understand if movements in price are supported by significant volume
    
    vpt = []
    day = []
    daily_change = 0
    daily_vpt = 0

    for x in range(0,len(df)-1):
        daily_change = (df["Adj Close Price"][x+1]-df["Adj Close Price"][x])/df["Adj Close Price"][x]
        daily_vpt = daily_vpt + df["Volume"][x+1]*daily_change              
        vpt.append(daily_vpt)
        day.append(df["Date"][x+1])
    
    return day, vpt


##########################################################
# Descriptive Statistics


def pullMaxValue(df):
    '''Returns maximum stock price over period - may be intraday'''
    
    value = df["High Price"].max()
    
    for x in range(0, len(df)):
        if value == df["High Price"][x]:
            date = df["Date"][x]
    
    return [value, date]


def pullMinValue(df):
    '''Returns minimum stock price over period - may be intraday'''
    
    value = df["Low Price"].min()
    
    for x in range(0, len(df)):
        if value == df["Low Price"][x]:
            date = df["Date"][x]
    
    return [value, date]


def calcVolatility(df):
    '''Returns the stock volatility over the period'''

    #based on adjusted close price

    mean = df["Adj Close Price"].mean()
    n = df["Adj Close Price"].count()-1
    volatility = 0

    for x in range(0,len(df)):
        volatility += (mean-df["Adj Close Price"][x])**2

    volatility = round(volatility/n,2) 

    return volatility


def calcStandardDeviation(df):
    '''Calculates the standard deviation over the period'''
    
    std = round(sqrt(calcVolatility(df)),2)

    return std


def calcPeriodReturn(df, beg, end):
    '''Returns closing share price for the period'''
    
    beginning_price = df["Open Price"][beg]
    closing_price = df["Adj Close Price"][end]

    period_return = round((closing_price - beginning_price)/beginning_price,4)

    return period_return

def formatCurrency(df_col):
    '''Returns list of data frame column in currency format'''
    
    new_list = []
    
    for x in range(0,len(df_col)):
        new_list.append("${:,.2f}".format(df_col[x]))
    
    return new_list

def formatCommaNumber(df_col):
    '''Returns list of data frame column in comma format'''
    
    new_list = []
    
    for x in range(0,len(df_col)):
        new_list.append("{:,.2f}".format(df_col[x]))
    
    return new_list

def formatPercent(df_col):
    '''Returns list of data frame column in comma format'''
    
    new_list = []
    
    for x in range(0,len(df_col)):
        y = df_col[x]*100
        new_list.append("{:,.2f}%".format(y))
    
    return new_list

def calcAdjustedPeriod(df_col, length):
    '''Returns an adjusted length list'''
    
    new_list = []
    
    for x in range(0, length):
        new_list.append(df_col[x])
    
    return new_list 
        
#We Should consider removing unless we use it for longterm stats
def calcDescriptiveStats(df):
    descStats = df.summary()
    
    return descStats


def calcComparativeStats(df):
    '''Calculates %Change over the prior period'''
    
    
    return 


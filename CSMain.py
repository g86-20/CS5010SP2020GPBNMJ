# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 20:57:58 2020

@author: Jon Baynes
"""

#%%writefile CS_StockData.py

import requests
from bs4 import BeautifulSoup
from time import sleep
from datapackage import Package
import csv 
import pandas as pd
import numpy as np
import re

def getStockData(user_input):
    '''Pulls data from Yahoo Finance'''
    pullStockInformationList()

    tickers = cleanUserStockInput(user_input)
    
    stockData = {}
    stockNames = {}
    
    for stock in tickers:
        try:
            stock_url = "https://finance.yahoo.com/quote/"+stock+"/history?p="+stock+""
            r = requests.get(stock_url)
            data = r.text
            soup = BeautifulSoup(data,features="lxml")

            contents = []

            for row in soup.find_all('tbody'):    
                for srow in row.find_all('tr'):
                    for content in srow.find_all('td'):
                        if "Dividend" in content.text:
                            #removes prior entry of date of dividend data point and ignores dividend data point
                            contents.pop() 
                            continue
                        else:
                            contents.append(content.text)
            
            stockData[stock] = defineStockData(contents)
            stockNames[stock] = defineStockName(stock)

        except:
            continue
            #stockErrors.append(stock)
            
        #delay added to avoid triggering web scrapping blocks
        delay = [0.1, 0.5, 1, 2, 2.5]
        delay = np.random.choice(delay)

        sleep(delay)
    
    return stockNames, stockData


def defineStockData(raw_list):
    '''Transforming scraped stock data into columns of data'''

    #the 7 columns of data, decided not to include most in this analysis
    date=[]
    open_price=[]
    high_price=[]
    low_price=[]
    close_price=[]
    adj_close_price=[]
    volume = []
    percent_change = []
    normalized_returns = []

    #pulled all data into one long list, but there are 7 columns of data
    #list comprehension to break out the full list in groupings by the 7 columns
    adj_contents = [raw_list[i * 7:(i + 1) * 7] for i in range((len(raw_list) + 7 - 1) // 7 )]

    #assigning the values to the columns
    for i in range(0, len(adj_contents)): #change to a count for amount of days requested...up to 97
        date.append(adj_contents[i][0])
        open_price.append(float(adj_contents[i][1].replace(",","")))
        high_price.append(float(adj_contents[i][2].replace(",","")))
        low_price.append(float(adj_contents[i][3].replace(",","")))
        close_price.append(float(adj_contents[i][4].replace(",","")))
        adj_close_price.append(float(adj_contents[i][5].replace(",","")))
        volume.append(float(adj_contents[i][6].replace(",","")))

    #calculating the percent change from prior close to today        
    for j in range(0, len(adj_close_price)):
        if j == len(adj_close_price)-1:
            percent_change.append(0.00)
        else:
            percent_change.append(round(adj_close_price[j]/adj_close_price[j+1]-1,3))

    #normalizing returns for comparison across companies
    normalizer = 100

    for x in range(len(percent_change), 0,-1):
        if x == len(percent_change):
            normalized_returns.append(normalizer)
        else:
            normalizer = round(normalizer * (1+percent_change[x-1]),3)
            normalized_returns.append(normalizer)

    normalized_returns.reverse()

    return addStockToDF(date, open_price, high_price, low_price, close_price, adj_close_price, volume, percent_change,normalized_returns)



def addStockToDF(date,open_price,high_price,low_price,close_price,adj_close_price,volume, percent_change,normalized_returns):
    '''Placing stock data into panda data frame'''
    #placing the values into a panda data frame
    x = pd.DataFrame({"Date": date,
                      "Open Price": open_price,
                      "High Price": high_price,
                      "Low Price": low_price,
                      "Close Price": close_price,
                      "Adj Close Price": adj_close_price,
                      "Volume":volume,
                      "Percent Change": percent_change,
                      "Normalized Returns": normalized_returns})
    x["Date"] = pd.to_datetime(x["Date"]) #allows interpretation as dates vs. ordered numbers

    #placing data frame into dictionary with stock ticker as key
    return x



def cleanUserStockInput(tickers):
    '''Cleans and formats user stock input'''
    tickers = tickers.split(",")

    #clean up white space and make all tickers upper case
    for x in range(0,len(tickers)):
        tickers[x] = tickers[x].strip()
        tickers[x] = tickers[x].upper()
        
    if len(tickers) > 1:
        tickers.append('%5EGSPC')

    return tickers
    

def defineStockName(ticker):
    '''Matches ticker with company name from CSV file'''
    
    #list obtained from https://dumbstockapi.com/
    stockList = pd.read_csv("StockInformationList.csv")
        
    for y in range(0, len(stockList)):
        if ticker == stockList["ticker"][y]:
            return stockList["name"][y]     
        elif ticker == "%5EGSPC":
            return "S&P 500"


def pullStockInformationList():
    '''Downloads CSV file of Ticker:Copmany Name'''
    
    #Download S&P 500 Stock List to Store Locally
    package = Package('https://datahub.io/core/s-and-p-500-companies/datapackage.json')

    #Initialize list for conslidating all tickers
    referenceList = []

    #Add each ticker to the list
    for resource in package.resources:
        if resource.descriptor['datahub']['type'] == 'derived/csv':
            referenceList.append(resource.read())

    #Create Dataframe then transpose
    stockSheet = pd.DataFrame(referenceList).T

    #Save the data locally for reference
    stockDF = pd.DataFrame(stockSheet[0].tolist(),columns=['ticker','name','sector'])
    stockDF.to_csv('StockInformationList.csv',mode='w',header=True)
    
import pandas as pd
import numpy as np
from math import sqrt


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
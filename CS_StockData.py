# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 20:51:14 2020

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

    tickerCheck = pullStockInformationList()
    
    tickerCheckFinal = tickerCheck + ['%5EGSPC']
    
    tickers = cleanUserStockInput(user_input)

    validTickers = []

    for stock in tickers:
        if stock not in tickerCheckFinal:
            print("Sorry, we don't recognize "+stock+ ". Please enter a valid ticker from the S&P 500.")
            return "stop","stop"
        else:
            validTickers.append(stock)
            
    stockData = {}
    stockNames = {}

    for stock in validTickers:
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

    validStocks = stockDF['ticker'].tolist()

    return validStocks


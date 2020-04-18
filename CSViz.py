# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 06:22:33 2020

@author: Jon Baynes
"""

#%%writefile CS_Graphing.py
import CSMain as cs
import csv 
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

#from CS_DataProcessing import *

def showTableData(df, ticker):
    '''Table displaying all columns of stock data'''

    date_values = df[ticker]["Date"].dt.strftime('%m/%d/%Y')
    open_price = cs.formatCurrency(df[ticker]["Open Price"])
    high_price = cs.formatCurrency(df[ticker]["High Price"])
    low_price = cs.formatCurrency(df[ticker]["Low Price"])
    close_price = cs.formatCurrency(df[ticker]["Close Price"])
    adj_close = cs.formatCurrency(df[ticker]["Adj Close Price"])
    volume = cs.formatCommaNumber(df[ticker]["Volume"])
    percent = cs.formatPercent(df[ticker]["Percent Change"])
    normalized = cs.formatCurrency(df[ticker]["Normalized Returns"])
        
    fig = go.Figure(data=[go.Table(header=dict(values=list(df[ticker].columns),
                align='center'),
                cells=dict(values=[date_values,open_price,high_price,low_price,close_price,adj_close,volume,percent,normalized],
                align='right'))
                ])

    fig.update_layout(autosize=False, width=1200,height=900, margin=dict(
        l=50,
        r=50,
        b=50,
        t=100,
        pad=4
    ))

    fig.update_layout(title='Data Table for {}'.format(format(cs.defineStockName(ticker))))

    fig.show()    

    
def graphSingleStockDefault(df,ticker):
    '''Default Graph for a single stock of price performance and volume'''
    #only for use in presentation - not dynamic due to titles/layout adjustments
    buildSingleStockLineChart(df, ticker)
    buildSingleStockVolumeBarChart(df,ticker)

    
def buildSingleStockLineChart(df, ticker):
    '''Creates a line graph of the adjusted close price for a single stock'''
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[ticker]['Date'], y=cs.formatCurrency(df[ticker]['Adj Close Price']),
                                    mode='lines',
                                    name=cs.defineStockName(ticker))) 
    fig.update_layout(title='Historical Price and Volume Trends for '+cs.defineStockName(ticker),
                       xaxis_title='Date',
                       yaxis_title='Adjusted Close Price', yaxis=dict(tickformat ="$.2"))
    
    fig.update_layout(autosize=False, width=1200,height=600, margin=dict(
        l=50,
        r=50,
        b=20,
        t=100,
        pad=4
    ))
    
    fig.show()

    
def buildSingleStockVolumeBarChart(df,ticker):
    '''Builds volume bar graph'''
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[ticker]['Date'],y=df[ticker]['Volume']))
    fig.update_layout(xaxis_title='Date', yaxis_title='Daily Trading Volume')

    fig.update_layout(autosize=False, width=1200,height=300, margin=dict(
        l=50,
        r=50,
        b=80,
        t=10,
        pad=4
    ))
    
    fig.show()  

    
def graphSingleStockPrediction(df, ticker, fast=12, slow=26, macd=9):
    '''Stacked charts of historical price and MACD'''
    #provides default values for the MACD analysis
    
    length = len(df[ticker]["Date"])-slow-macd
    buildSingleStockLineCharts2(df,ticker,length)
    graphMACD_buy_sell2(df, ticker, fast, slow, macd)


def buildSingleStockLineCharts2(df, ticker, length):
    '''Creates a line graph of the adjusted close price for a single stock'''
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[ticker]['Date'], y=cs.formatCurrency(df[ticker]['Adj Close Price']),
                                    mode='lines',
                                    name=cs.defineStockName(ticker))) 
    fig.update_layout(title='Historical Price and MACD Trends for '+cs.defineStockName(ticker),
                       xaxis_title='Date',
                       yaxis_title='Adjusted Close Price', yaxis=dict(tickformat ="$.2"))
    
    fig.update_layout(autosize=False, width=1200,height=600, margin=dict(
        l=50,
        r=50,
        b=20,
        t=100,
        pad=4
    ))
    
    fig.update_layout(shapes=[
        dict(
          type= 'line',
          yref= 'paper', y0= 0, y1= 1,
          xref= 'x', x0= df[ticker]["Date"][(length)], x1= df[ticker]["Date"][(length)],
          line=dict(
              color="Gray",
              width=2,
              dash="dash",
          )
        )
    ])
    

    fig.add_annotation(
                    x=df[ticker]["Date"][(length)],
                    y=df[ticker]["Adj Close Price"].min(),
                    text="MACD Analysis Range Begins",
                    textangle=90)
    
    fig.show()


def graphMACD_buy_sell2(df, ticker, fast, slow, macd):
    '''Simplifying MACD graph call by ticker'''

    ma_fast, ma_slow = cs.calcMACD(df[ticker]["Adj Close Price"], fast, slow, macd)
    macd_index = cs.pullMACDPoints(ma_fast, ma_slow)
    
    ma_fast2, ma_slow2 = cs.calcMACDForGraphs(df[ticker]["Adj Close Price"], fast, slow, macd)
   
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[ticker]["Date"], y=ma_fast2,
                        mode='lines',
                        name='fast MA'))
    fig.add_trace(go.Scatter(x=df[ticker]["Date"], y=ma_slow2,
                        mode='lines',
                        name='slow MA'))

    for x in range(0, len(macd_index)):
        fig.add_annotation(
                    x=df[ticker]["Date"][macd_index[x][0]],
                    y=ma_slow2[macd_index[x][0]],
                    text=macd_index[x][1])

    fig.update_annotations(dict(
                xref="x",
                yref="y",
                showarrow=True,
                arrowhead=7,
                ax=0,
                ay=-40
    ))

    fig.update_layout(autosize=False, width=1200,height=300, margin=dict(
        l=50,
        r=50,
        b=80,
        t=10,
        pad=4
    ))
    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Moving Average Difference', yaxis=dict(tickformat ="$.2"))
    
    fig.update_layout(legend_orientation="h")
    
    fig.update_layout(shapes=[
        dict(
          type= 'line',
          yref= 'paper', y0= 0, y1= 1,
          xref= 'x', x0= df[ticker]["Date"][(len(df[ticker]["Date"])-slow-macd)], x1= df[ticker]["Date"][(len(df[ticker]["Date"])-slow-macd)],
          line=dict(
              color="Gray",
              width=2,
              dash="dash",
          )
        )
    ])  

    fig.show()

    
def graphMultipleStockDefault(df):
    '''Default Graph for a multiple stock comparitive performance and table'''
    #only for use in presentation - not dynamic due to titles/layout adjustments
    buildMultiStockLineGraph2(df)
    buildStatsTable2(df)


def buildMultiStockLineGraph2(df):
    '''Creates a line graph of the normalized returns for several stocks'''
    symbols = list(df.keys())
    fig = go.Figure()
    for symbol in symbols:
        if symbol == "%5EGSPC":
            fig.add_trace(go.Scatter(x=df[symbol]['Date'], y=df[symbol]['Normalized Returns'],
                                    mode='lines',
                                    marker = dict(color="Gray"),
                                    name="S&P 500")) 
        else: 
            fig.add_trace(go.Scatter(x=df[symbol]['Date'], y=df[symbol]['Normalized Returns'],
                                    mode='lines',
                                    name=symbol)) 
    fig.update_layout(title='Historical Normalized Returns for Selected Stocks',
                       xaxis_title='Date',
                       yaxis_title='Normalized Returns - Base 100')
    fig.update_layout(showlegend=True)
    fig.update_layout(autosize=False, width=1200,height=600, margin=dict(
        l=50,
        r=50,
        b=20,
        t=100,
        pad=4
    ))
    
    fig.update_layout(legend_orientation="h")
        
    fig.show()
    
def buildStatsTable2(df):
    '''Table displaying descriptive statistics for stocks'''
    symbols = list(df.keys())
    names = []
    period_return = []
    relative_return = []
    maxVals = []
    minVals = []
    stdevs = []
    
    # gets the descriptive statistics for all of the stocks entered:
    for symbol in symbols:
        names.append(cs.defineStockName(symbol))
        period_return.append(cs.calcPeriodReturn(df[symbol],(len(df[symbol])-1),0))
        
        if symbol == "%5EGSPC":
            relative_return.append(0)
        else:
            relative_return.append(cs.calcPeriodReturn(df[symbol],(len(df[symbol])-1),0)-cs.calcPeriodReturn(df["%5EGSPC"],(len(df["%5EGSPC"])-1),0))
        maxVal, maxDate = cs.pullMaxValue(df[symbol])
        maxVals.append(maxVal)
        minVal, minDate = cs.pullMinValue(df[symbol])
        minVals.append(minVal)
        stdev = cs.calcStandardDeviation(df[symbol])
        stdevs.append(stdev)
        
    tableData = [names, cs.formatPercent(period_return), cs.formatPercent(relative_return), cs.formatCurrency(minVals), cs.formatCurrency(maxVals), cs.formatCurrency(stdevs)]
        
    fig = go.Figure(data=[go.Table(
                columnorder=[1,2,3,4,5,6],
                columnwidth=[150,80,80,80,80,80],
                header=dict(values=['Stock','Period Return', 'S&P Relative Return', 'Minimum Value', 'Maximum Value', 'Standard Deviation'],
                align='center'),
                cells=dict(values=tableData,
                align=['left','right']))
                ])

    fig.update_layout(autosize=False, width=1200, height = 300, margin=dict(
        l=50,
        r=50,
        b=80,
        t=60,
        pad=4
    ))

    fig.update_layout(title='Descriptive Statistics for Selected Stocks')

    fig.show()
    

    
    
#########################################################################################################    
############################# OLDER FILES BELOW #########################################################    
#########################################################################################################    



    
def buildVolumeBarChart(stockData):
    '''Builds volume bar graph'''
    symbols = list(stockData.keys())
    symbol = symbols[0]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=stockData[symbol]['Date'],y=stockData[symbol]['Volume']))
    fig.update_layout(title='Volume Bar Chart for '+symbol,
                   xaxis_title='Date',
                   yaxis_title='Trading Volume')
    fig.show()    
    
    
def buildMultiStockLineGraph(stockData):
    '''Creates a line graph of the normalized returns for several stocks'''
    symbols = list(stockData.keys())
    fig = go.Figure()
    for symbol in symbols:
        fig.add_trace(go.Scatter(x=stockData[symbol]['Date'], y=stockData[symbol]['Normalized Returns'],
                                    mode='lines',
                                    name=symbol)) 
    fig.update_layout(title='Normalized Returns for Selected Stocks',
                       xaxis_title='Date',
                       yaxis_title='Normalized Returns')
    fig.update_layout(showlegend=True)
    fig.show()

def buildSingleStockLineGraph(stockData):
    '''Creates a line graph of the adjusted close price for a single stock'''
    symbols = list(stockData.keys())
    fig = go.Figure()
    for symbol in symbols:
        fig.add_trace(go.Scatter(x=stockData[symbol]['Date'], y=stockData[symbol]['Adj Close Price'],
                                    mode='lines',
                                    name=symbol)) 
    fig.update_layout(title='Adjusted Close Price for '+symbol,
                       xaxis_title='Date',
                       yaxis_title='Adj Close Price')
    fig.show()
    
def buildStockAndWordLineGraph(stockData, wordData):
    # place holder
    pass

def buildMultiStockAndWordGraph(stockData, wordData):
    # place holder
    pass

def buildStatsTable(stockData):
    '''Table displaying descriptive statistics for stocks'''
    symbols = list(stockData.keys())
        
    maxVals = []
    maxDates = []
    minVals = []
    minDates = []
    volatils = []
    stdevs = []
#     pdRets = []
    
    # gets the descriptive statistics for all of the stocks entered:
    for symbol in symbols:
        maxVal, maxDate = cs.pullMaxValue(stockData[symbol])
        maxVals.append(maxVal)
        maxDates.append(maxDate.strftime('%m/%d/%Y'))
        minVal, minDate = cs.pullMinValue(stockData[symbol])
        minVals.append(minVal)
        minDates.append(minDate.strftime('%m/%d/%Y'))
        volatil = cs.calcVolatility(stockData[symbol])
        volatils.append(volatil)
        stdev = cs.calcStandardDeviation(stockData[symbol])
        stdevs.append(stdev)
#         pdRet = calcPeriodReturn(stockData[symbol], beginning, end)
#         pdRets.append(pdRet)
        
    tableData = [symbols, maxVals, maxDates, minVals, minDates, volatils, stdevs]
        
    fig = go.Figure(data=[go.Table(header=dict(values=['Stock', 'Maximum Value', 'Date of Max Val', 'Minimum Value', 'Date of Min Val', 'Volatility', 'Standard Deviation'],
                align='left'),
                cells=dict(values=tableData,
                align='left'))
                ])

    fig.update_layout(autosize=False, width=1200,height=500, margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ))

    fig.update_layout(title='Descriptive Statistics for Selected Stocks')

    fig.show()

def graphMACD_buy_sell(df, ticker, fast, slow, macd):
    '''Simplifying MACD graph call by ticker'''

    ma_fast, ma_slow = cs.calcMACD(df[ticker]["Adj Close Price"], fast, slow, macd)
    macd_index = cs.pullMACDPoints(ma_fast, ma_slow)
    x_axis = []

    for x in range(0,len(ma_slow)):
        x_axis.append(df[ticker]["Date"][x])
   
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_axis, y=ma_fast,
                        mode='lines',
                        name='fast MA'))
    fig.add_trace(go.Scatter(x=x_axis, y=ma_slow,
                        mode='lines',
                        name='slow MA'))

    for x in range(0, len(macd_index)):
        fig.add_annotation(
                    x=x_axis[macd_index[x][0]],
                    y=ma_slow[macd_index[x][0]],
                    text=macd_index[x][1])

    fig.update_annotations(dict(
                xref="x",
                yref="y",
                showarrow=True,
                arrowhead=7,
                ax=0,
                ay=-40
    ))

    fig.update_layout(title='MACD of {}'.format(cs.defineStockName(ticker)))

    fig.show()


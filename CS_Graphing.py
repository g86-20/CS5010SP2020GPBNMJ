# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 20:53:50 2020

@author: Jon Baynes
"""

#%%writefile CS_Graphing.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from CS_StockData import *
from CS_DataProcessing import *

#from CS_DataProcessing import *

def showTableData(df, ticker):
    '''Table displaying all columns of stock data'''

    date_values = df[ticker]["Date"].dt.strftime('%m/%d/%Y')
    open_price = formatCurrency(df[ticker]["Open Price"])
    high_price = formatCurrency(df[ticker]["High Price"])
    low_price = formatCurrency(df[ticker]["Low Price"])
    close_price = formatCurrency(df[ticker]["Close Price"])
    adj_close = formatCurrency(df[ticker]["Adj Close Price"])
    volume = formatCommaNumber(df[ticker]["Volume"])
    percent = formatPercent(df[ticker]["Percent Change"])
    normalized = formatCurrency(df[ticker]["Normalized Returns"])
        
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

    fig.update_layout(title='Data Table for {}'.format(format(defineStockName(ticker))))

    fig.show()    

    
def graphSingleStockDefault(df,ticker):
    '''Default Graph for a single stock of price performance and volume'''
    #only for use in presentation - not dynamic due to titles/layout adjustments
    buildSingleStockLineChart(df, ticker)
    buildSingleStockVolumeBarChart(df,ticker)

    
def buildSingleStockLineChart(df, ticker):
    '''Creates a line graph of the adjusted close price for a single stock'''
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[ticker]['Date'], y=formatCurrency(df[ticker]['Adj Close Price']),
                                    mode='lines',
                                    name=defineStockName(ticker))) 
    fig.update_layout(title='Historical Price and Volume Trends for '+defineStockName(ticker),
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
    fig.add_trace(go.Scatter(x=df[ticker]['Date'], y=formatCurrency(df[ticker]['Adj Close Price']),
                                    mode='lines',
                                    name=defineStockName(ticker))) 
    fig.update_layout(title='Historical Price and MACD Trends for '+defineStockName(ticker),
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

    ma_fast, ma_slow = calcMACD(df[ticker]["Adj Close Price"], fast, slow, macd)
    macd_index = pullMACDPoints(ma_fast, ma_slow)
    
    ma_fast2, ma_slow2 = calcMACDForGraphs(df[ticker]["Adj Close Price"], fast, slow, macd)
   
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
        names.append(defineStockName(symbol))
        period_return.append(calcPeriodReturn(df[symbol],(len(df[symbol])-1),0))
        
        if symbol == "%5EGSPC":
            relative_return.append(0)
        else:
            relative_return.append(calcPeriodReturn(df[symbol],(len(df[symbol])-1),0)-calcPeriodReturn(df["%5EGSPC"],(len(df["%5EGSPC"])-1),0))
        maxVal, maxDate = pullMaxValue(df[symbol])
        maxVals.append(maxVal)
        minVal, minDate = pullMinValue(df[symbol])
        minVals.append(minVal)
        stdev = calcStandardDeviation(df[symbol])
        stdevs.append(stdev)
        
    tableData = [names, formatPercent(period_return), formatPercent(relative_return), formatCurrency(minVals), formatCurrency(maxVals), formatCurrency(stdevs)]
        
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
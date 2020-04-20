# -*- coding: utf-8 -*-
"""
"""

import sys

from CS_StockData import *
from CS_Graphing import *
from CS_DataProcessing import *

def mainMenu():
    print("************MAIN MENU**************\n")
    choice = input("""
                      1: Stocks menu
                      2: Stocks and Google Analytics menu
                      3: Google Analytics menu   
                      0: Quit

                      Please enter your choice: """)
    # not sure if we want to include options 3 or 4
    if choice == "1":
        stocksMenu()
    elif choice == "2":
        stockAndWordMenu()
    elif choice == "3":
        wordsMenu()
    elif choice=="4":
        # add suggested stocks/word combinations? 
        # or just a general help menu?
        pass
    elif choice=="0":
        sys.exit
    else:
        print("\nPlease choose from options 1, 2, 3, or 4.")
        print("Please try again.\n")
        mainMenu()

def stocksMenu():
    print("\n************OPTION 1: STOCKS MENU**************\n")
    choice = input("""
                      What would you like to look at?
                      1: Single stock analysis 
                      2: Multiple stock comparison 
                      0: Return to main menu

                      Please enter your choice: """)
    if choice == "1":
        singleStockOptions()
        continueOrExit()
    elif choice == "2":
        multipleStockOptions()
        continueOrExit()
    elif choice=="0":
        mainMenu()
    else:
        print("\nPlease choose from options 1 or 2; or enter 0 to return to the main menu.")
        print("Please try again.\n")
        stocksMenu()
        
def stockAndWordMenu():
    print("\n************OPTION 2: STOCKS AND GOOGLE ANALYTICS MENU**************\n")
    choice = input("""
                      What would you like to look at?
                      1: Close-up comparison of a single stock and keyword
                      0: Return to main menu

                      Please enter your choice: """)
    if choice == "1":
        singleStocksingleWord()
        continueOrExit()
    elif choice=="0":
        mainMenu()
    else:
        print("\nPlease choose from options 1, 2, 3, or 4.")
        print("Please try again.\n")
        stockAndWordMenu()
        
def wordsMenu():
    pass

def singleStockOptions():
    symbol = input("Please enter a stock symbol: ")
    stockName, stockData = getStockData(symbol) # it won't return anything for AMZN (Amazon)? maybe do unit testing for this
    # add try-except loop for if stock symbol isn't valid? 
    
    if stockName != "stop":
        showTableData(stockData,stockName)
        graphSingleStockDefault(stockData,stockName)
        graphSingleStockPrediction(stockData,stockName)
    else:
        pass
    # def graphMACD_buy_sell(df, ticker, fast, slow, macd) ### add this later-- ask about the parameters
    
def multipleStockOptions():
    symbols = input("Please enter up to five stock symbols, separated by commas: ")
    stockNames, stockData = getStockData(symbols)
    
    if stockNames != "stop":
        graphMultipleStockDefault(stockData)
    else:
        pass
    

def singleStockSingleWord():
    symbol = input("Please enter a stock symbol: ")
    stockName, stockData = getStockData(symbol)
    word = input("Please enter a keyword: ")
    # call the function that will return the Google Analytics data here
    # buildStockAndWordLineGraph(stockData, wordData) -- this is an empty function in the graphing module right now

def continueOrExit():
    keepGoing = input("Would you like to look at something else? Y/N: ")
    keepGoing = keepGoing.upper()
    if keepGoing == "Y":
        mainMenu()
    elif keepGoing == "N":
        sys.exit
    else:
        print("Please enter Y for Yes or N for No.")
        continueOrExit()

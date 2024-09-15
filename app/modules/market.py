from app.helpers.logger import logger
import yfinance as yf
from datetime import datetime

logger.info("Initializing Markets.")
tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'V']
logger.success("Successfully initialized Markets.")

def getMarketData():
    marketData = {}

    for ticker in tickers:
        
        tickerData = yf.Ticker(ticker)

        end_date = datetime.now().strftime('%Y-%m-%d')

        # get all stock info
        tickerData = tickerData.history(start='2024-03-15', end=end_date)
        tickerHistory = {}
        prevDate = '20240315'

        for date in (tickerData.index):
            date = str('%04d' % date.year) + str('%02d' % date.month) + str('%02d' % date.day)
            tickerHistory[date] = {}
            for category in tickerData.iloc[0,:].index:
                info = tickerData.loc[date,:][category]
                tickerHistory[date][category] = info
            
            tickerHistory[date]['Change $'] = tickerHistory[date]['Close'] - tickerHistory[prevDate]['Close']
            tickerHistory[date]['Change %'] = tickerHistory[date]['Change $'] / tickerHistory[prevDate]['Close']
            prevDate = date

        marketData[ticker] = tickerHistory

    logger.info(f"Retrieved market data for {len(marketData)} tickers")
    return marketData

import yfinance as yf
from datetime import datetime

from src.utils.logger import logger
from src.utils.response import Response

logger.announcement('Initializing Markets', 'info')
tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'V']
logger.announcement('Successfully initialized Markets', 'success')

def get_current_data(ticker):
    try:
        tickerData = yf.Ticker(ticker)
        return Response.success(tickerData.info)
    except Exception as e:
        logger.error(f'Error getting current market data for {ticker}: {e}')
        return Response.error(f'Error getting current market data for {ticker}: {e}')

def get_historical_data(tickers):

    logger.info(f'Getting historical market data for tickers: {tickers}')
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

    logger.success(f"Successfully retrieved market data for {len(tickers)} tickers")
    return Response.success(marketData)




from ib_insync import *
from src.utils.exception import handle_exception
from src.utils.logger import logger
from src.utils.connectors.tws import TWSConnector

logger.announcement("Initializing Market Data Service", 'info')
logger.announcement("Market Data Service initialized", 'success')

tws = TWSConnector()

@handle_exception
def latest_stock_data(symbol: str):
    logger.info(f"Fetching latest price for {symbol}")
    contract = Stock(symbol, 'SMART', 'USD')
    return tws.current_data(contract)

@handle_exception
def historical_stock_price(symbol: str, period: str = '1 Y'):
    logger.info(f"Fetching historical data for {symbol}")
    contract = Stock(symbol, 'SMART', 'USD')
    return tws.historical_data(contract, period)
from ib_insync import Contract
from src.utils.exception import handle_exception
from src.utils.logger import logger
from src.utils.connectors.tws import TWSConnector

logger.announcement("Initializing Account Service", 'info')
logger.announcement("Account Service initialized", 'success')

tws = TWSConnector()

@handle_exception
def summary():
    logger.info(f"Fetching account summary information")
    return tws.account_summary()

@handle_exception
def positions():
    logger.info(f"Fetching account positions information")
    return tws.positions()

@handle_exception
def portfolio():
    logger.info(f"Fetching account portfolio information")
    return tws.portfolio()

@handle_exception
def pnl():
    logger.info(f"Fetching account PNL information")
    return tws.pnl()

@handle_exception
def pnl_single(contract: Contract):
    logger.info(f"Fetching account PNL for {contract} information")
    return tws.pnl_single(contract)
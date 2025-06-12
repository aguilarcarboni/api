from src.utils.exception import handle_exception
from src.utils.connectors.tws import TWSConnector
from src.utils.logger import logger

tws = TWSConnector()

logger.announcement('Initializing Trading Service', type='info')
logger.announcement('Initialized Trading Service', type='success')

@handle_exception
def get_account_summary():
    return tws.get_account_summary()
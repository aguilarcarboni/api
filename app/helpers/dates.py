import pytz

from app.helpers.location import location
from app.helpers.logger import logger

from datetime import datetime
from pandas.tseries.offsets import BDay

logger.announcement("Initializing Date and Time.", 'info')
logger.announcement("Successfully initialized Date and Time.", 'success')

def getLastWorkingDate():
    timezone_time = datetime.now(location.timezone)
    last_working_date = (timezone_time - BDay(1)).strftime('%Y%m%d')
    return last_working_date
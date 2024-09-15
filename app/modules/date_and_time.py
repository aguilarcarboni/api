from app.modules.location import location
from app.helpers.logger import logger

from datetime import datetime
from pandas.tseries.offsets import BDay

logger.info("Initializing Date and Time.")
logger.success("Successfully initialized Date and Time.")

def getCurrentTime():
    currentDateTime = datetime.now(location.timezone)
    currentTime = currentDateTime.strftime("%I:%M%p")
    return currentTime

def getCurrentDate():
    currentDateTime = datetime.now(location.timezone)
    currentDate = currentDateTime.strftime("%A %B %d %Y")
    return currentDate

def getLastWorkingDate():
    timezone_time = datetime.now(location.timezone)
    last_working_date = (timezone_time - BDay(1)).strftime('%Y%m%d')
    return last_working_date
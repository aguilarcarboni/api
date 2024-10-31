import pytz

from app.helpers.logger import logger

class Location:
    def __init__(self):
        logger.announcement('Initializing Location', 'info')
        self.coordinates = {'lat': 9.9281, 'lon': -84.2376}
        self.timezone = pytz.timezone('America/Costa_Rica')
        logger.announcement('Successfully initialized Location', 'success')

location = Location()
import pytz

from app.helpers.logger import Logger

logger = Logger()

class Location:
    def __init__(self):
        logger.info("Initializing Location.")
        self.coordinates = {'lat': 9.9281, 'lon': -84.2376}
        self.timezone = pytz.timezone('America/Costa_Rica')
        logger.success("Successfully initialized Location.")

location = Location()
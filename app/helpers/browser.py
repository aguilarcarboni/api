from bs4 import BeautifulSoup
from app.helpers.logger import logger
from app.helpers.response import Response
import requests as rq

class Browser:
    def __init__(self):
        logger.announcement('Initializing Browser', 'info')
        logger.announcement('Successfully initialized Browser', 'success')

    def scraper(self, url):
        logger.info(f"Scraping URL: {url}")
        # Send a request to fetch the HTML content
        response = rq.get(url)
        if response.status_code != 200:
            logger.error("Failed to retrieve the web page.")
            return Response.error("Failed to retrieve the web page.")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        logger.success("Successfully scraped URL.")
        return soup

from bs4 import BeautifulSoup
from app.helpers.logger import logger
from app.helpers.response import Response
import requests as rq
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class Browser:
    def __init__(self):
        logger.announcement('Initializing Browser', 'info')
        self.robot_parser = RobotFileParser()
        logger.announcement('Successfully initialized Browser', 'success')

    def _can_fetch(self, url: str) -> bool:
        """Check if scraping is allowed for the given URL."""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
            return self.robot_parser.can_fetch("*", url)
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")
            return False

    def scraper(self, url: str) -> BeautifulSoup | Response:

        logger.info(f"Scraping URL: {url}")
        
        # Check robots.txt rules first
        if not self._can_fetch(url):
            logger.error("Scraping not allowed according to robots.txt rules")
            return Response.error("Scraping not allowed for this URL")

        # Send a request to fetch the HTML content
        response = rq.get(url)
        if response.status_code != 200:
            logger.error("Failed to retrieve the web page.")
            return Response.error("Failed to retrieve the web page.")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        logger.success(f"Successfully scraped {url}.")
        return soup
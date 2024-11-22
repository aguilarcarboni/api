from bs4 import BeautifulSoup
import requests as rq
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

from src.utils.logger import logger
from src.utils.response import Response

# TODO CACHE SCRAPED PAGES

class Browser:
    
    def __init__(self):
        logger.announcement('Initializing Browser', 'info')
        self.robot_parser = RobotFileParser()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Jawa/1.0; +http://laserfocus.space/bot)'
        }
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

        logger.warning(f"Scraping URL: {url}")
        
        # Check robots.txt rules first
        if not self._can_fetch(url):
            logger.error("Scraping not allowed according to robots.txt rules")
            return Response.error("Scraping not allowed for this URL")

        # Send a request with headers
        response = rq.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error("Failed to retrieve the web page.")
            return Response.error("Failed to retrieve the web page.")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        logger.success(f"Successfully scraped {url}.")
        return soup
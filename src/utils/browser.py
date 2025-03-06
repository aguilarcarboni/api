from bs4 import BeautifulSoup
import requests as rq
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import os

from src.utils.logger import logger
from src.utils.response import Response

class Browser:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.announcement('Initializing Browser', 'info')
            cls._instance = super(Browser, cls).__new__(cls)
            cls._instance.robot_parser = RobotFileParser()
            cls._instance.headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; Jawa/1.0; +http://api.laserfocus.space/bot)'
            }
            logger.announcement('Successfully initialized Browser', 'success')
        return cls._instance
    
    def __init__(self):
        pass

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

    def scraper(self, url: str):

        logger.info(f"Scraping URL: {url}")
        
        # Check robots.txt rules first
        if not self._can_fetch(url):
            logger.error("Scraping not allowed according to robots.txt rules")
            return Response.error("Scraping not allowed for this URL")
    
        if (url.endswith('.html')):
            file_name = urlparse(url).netloc + urlparse(url).path.replace('/', '_')
        else:
            file_name = urlparse(url).netloc + urlparse(url).path.replace('/', '_') + '.html'

        # Send a request with headers
        if file_name in os.listdir(os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'websites')):
            logger.info(f"Cached content for URL exists.")
            with open(os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'websites', file_name), 'r', encoding='utf-8') as cache_file:
                soup = BeautifulSoup(cache_file.read(), 'html.parser')
                logger.success(f"Retrieved existing cached content for URL.\n")
                return soup

        response = rq.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error("Failed to retrieve the web page.")
            return Response.error("Failed to retrieve the web page.")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Caching the scraped content
        cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'websites')
        os.makedirs(cache_dir, exist_ok=True)

        cache_file_path = os.path.join(cache_dir, file_name)
        with open(cache_file_path, 'w', encoding='utf-8') as cache_file:
            cache_file.write(soup.prettify())
            logger.success(f"Saved cached content for URL.")

        logger.success(f"Successfully scraped URL.\n")
        return soup

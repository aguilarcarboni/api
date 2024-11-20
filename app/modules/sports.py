import requests
from app.helpers.logger import logger

class ESPN:

    def __init__(self):
        logger.announcement('ESPN module initializing', 'info')
        logger.announcement('ESPN module initialized', 'success')

    def get_nfl_scoreboard(self):
        logger.info('Fetching NFL scoreboard')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard')
        logger.success('NFL scoreboard fetched')
        return response.json()
    
    def get_nfl_news(self):
        logger.info('Fetching NFL news')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/news')
        logger.success('NFL news fetched')
        return response.json()
    
    def get_nba_news(self):
        logger.info('Fetching NBA news')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news')
        logger.success('NBA news fetched')
        return response.json()
    
    def get_nba_scoreboard(self):
        logger.info('Fetching NBA scoreboard')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard')
        logger.success('NBA scoreboard fetched')
        return response.json()
    
    def get_scoreboard(self):
        logger.info('Fetching scoreboard')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/scoreboard')
        logger.success('Scoreboard fetched')
        return response.json()
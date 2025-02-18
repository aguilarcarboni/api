import requests
from src.utils.logger import logger
from src.utils.response import Response

class ESPN:

    def __init__(self):
        logger.announcement('ESPN module initializing', 'info')
        logger.announcement('ESPN module initialized', 'success')

    def get_nfl_scoreboard(self):
        try:
            logger.info('Fetching NFL scoreboard')
            response = requests.get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard')
            logger.success('NFL scoreboard fetched')
            return Response.success(response.json())
        except Exception as e:
            logger.error(f'Error fetching NFL scoreboard: {e}')
            return Response.error(f'Error fetching NFL scoreboard: {e}')
    
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
        try:
            logger.info('Fetching NBA scoreboard')
            response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard')
            logger.success('NBA scoreboard fetched')
            return Response.success(response.json())
        except Exception as e:
            logger.error(f'Error fetching NBA scoreboard: {e}')
            return Response.error(f'Error fetching NBA scoreboard: {e}')
    
    def get_scoreboard(self):
        logger.info('Fetching scoreboard')
        response = requests.get('https://site.api.espn.com/apis/site/v2/sports/scoreboard')
        logger.success('Scoreboard fetched')
        return response.json()
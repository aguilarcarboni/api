import os
import base64
import requests
from urllib.parse import urlencode
from app.helpers.logger import logger
from app.helpers.response import Response

class Spotify:

    def __init__(self):
        self.auth_url = 'https://accounts.spotify.com/authorize'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.authenticated = False

    def authenticate(self):
        logger.info('Authenticating with Spotify...')
        response = requests.get('https://accounts.spotify.com/authorize')
        if response.status_code == 200:
            print(response.json())
            logger.success('Successfully authenticated with Spotify')
            return Response.success(response.json())
        else:
            logger.error('Failed to authenticate with Spotify')
            return Response.error(response.json())
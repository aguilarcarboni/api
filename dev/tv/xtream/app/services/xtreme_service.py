import requests
from flask import current_app
from app.utils.helpers import handle_api_error

class XtremeService:
    def __init__(self):
        self.base_url = "http://flytv.club:8080"
        self.username = "aguilarcarboni"
        self.password = "Bz4kxMcWuN"

    @handle_api_error
    def authenticate(self):
        url = f"{self.base_url}/player_api.php"
        params = {
            "username": self.username,
            "password": self.password
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @handle_api_error
    def get_live_streams(self):
        url = f"{self.base_url}/player_api.php"
        params = {
            "username": self.username,
            "password": self.password,
            "action": "get_live_streams"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @handle_api_error
    def get_vod_streams(self):
        url = f"{self.base_url}/player_api.php"
        params = {
            "username": self.username,
            "password": self.password,
            "action": "get_vod_streams"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @handle_api_error
    def get_series(self):
        url = f"{self.base_url}/player_api.php"
        params = {
            "username": self.username,
            "password": self.password,
            "action": "get_series"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @handle_api_error
    def get_epg(self, stream_id):
        url = f"{self.base_url}/player_api.php"
        params = {
            "username": self.username,
            "password": self.password,
            "action": "get_short_epg",
            "stream_id": stream_id
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
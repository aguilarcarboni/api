import os
import requests
import re
from src.utils.logger import logger
from src.utils.response import Response
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from src.utils.database import DatabaseHandler

logger.announcement('Initializing TV Service', 'info')

Base = declarative_base()

class TV(Base):
    """TV table"""
    __tablename__ = 'tv'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stream_id = Column(String)
    name = Column(String)
    title = Column(String)
    stream_type = Column(String)
    type_name = Column(String)
    stream_icon = Column(String)
    epg_channel_id = Column(String)
    category_name = Column(String)
    category_id = Column(String)
    live = Column(String)
    favorite = Column(Boolean, default=False)
    added = Column(String)
    updated = Column(String)
    created = Column(String)

class Credentials(Base):
    """Credentials table"""
    __tablename__ = 'credentials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    password = Column(String)
    url = Column(String)
    created = Column(String)
    updated = Column(String)

db_name = 'tv'
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', f'{db_name}.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

"""
XTREAM_BASE_URL = "http://xdplayer.tv:8080"
XTREAM_USER = "aguilarcarboni"
XTREAM_PASS = "pXU2Hx6NMu"
"""

logger.announcement('Successfully initialized TV Service', 'success')

def fetch_channels_from_provider(user_id: int):
    logger.info('Fetching playlist...')

    # Get user credentials
    credentials = db.read('credentials', {'user_id': user_id})
    if credentials['status'] != 'success':
        logger.error('Failed to fetch credentials')
        return Response.error('Failed to fetch credentials')
    
    if len(credentials['content']) != 1:
        logger.error('Credentials error')
        return Response.error('Credentials error')
    
    url = credentials['content'][0]['url']
    username = credentials['content'][0]['username']
    password = credentials['content'][0]['password']

    # Clear current tv channels
    db.delete_all('tv')

    # Get all streams in m3u8 format
    all_streams_url = f"/panel_api.php?username={username}&password={password}&type=m3u_plus&output=m3u8"
    streams_response = requests.get(url + all_streams_url)
    if streams_response.status_code != 200:
        logger.error(f'Failed to fetch playlist: {streams_response.status_code}')
        return Response.error(f'Failed to fetch playlist: {streams_response.status_code}')

    streams = streams_response.json()
    
    if 'available_channels' not in streams:
        logger.error('Invalid response format')
        return Response.error('Invalid response format')

    # Process and save each channel
    for channel_id, channel_data in streams['available_channels'].items():
        channel = {
            'stream_id': channel_data.get('stream_id'),
            'name': channel_data.get('name'),
            'title': channel_data.get('title'),
            'stream_type': channel_data.get('stream_type'),
            'type_name': channel_data.get('type_name'),
            'stream_icon': channel_data.get('stream_icon'),
            'epg_channel_id': channel_data.get('epg_channel_id'),
            'category_name': channel_data.get('category_name'),
            'category_id': channel_data.get('category_id'),
            'live': channel_data.get('live'),
            'added': channel_data.get('added'),
            'favorite': False
        }
        
        db.create('tv', channel)

    logger.success('Playlist fetched successfully')
    logger.info('Saving playlist to cache and database...')
    logger.announcement('Playlist saved successfully', 'success')
    return Response.success('Playlist saved successfully')

def create_credentials(user_id: int, url: str, username: str, password: str):
    db.create('credentials', {
        'user_id': user_id,
        'url': url,
        'username': username,
        'password': password
    })
    return Response.success('Credentials created successfully')

def get_credentials(user_id: int):
    return db.read('credentials', {'user_id': user_id})

def get_channels():
    return db.read('tv')

def favorite_channel(stream_id: str):
    db.update(table='tv', data={'favorite': True}, params={'stream_id': stream_id})
    return Response.success('Channel favorited successfully')

def unfavorite_channel(stream_id: str):
    db.update(table='tv', data={'favorite': False}, params={'stream_id': stream_id})
    return Response.success('Channel unfavorited successfully')
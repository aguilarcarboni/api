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
    url = Column(String)
    xui_id = Column(String)
    tvg_id = Column(String)
    tvg_name = Column(String)
    tvg_logo = Column(String)
    group_title = Column(String)
    favorite = Column(Boolean, default=False)
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

    print(credentials)

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
    get_all_streams = f"/get.php?username={username}&password={password}&type=m3u_plus&output=m3u8"
    response = requests.get(url + get_all_streams)
    if response.status_code != 200:
        logger.error(f'Failed to fetch playlist: {response.status_code}')
        return Response.error(f'Failed to fetch playlist: {response.status_code}')
    logger.success('Playlist fetched successfully')

    logger.info('Saving playlist to cache and database...')
    playlist_path = os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'tv', 'playlist.m3u')
    if not os.path.exists(playlist_path):
        os.makedirs(os.path.dirname(playlist_path))

    with open(playlist_path, 'w', encoding='utf-8') as f:
        lines = response.text.splitlines()
        xui_id = ''
        tvg_id = ''
        tvg_name = ''
        tvg_logo = ''
        group_title = ''
        
        for i, line in enumerate(lines):
            if i % 100 == 0:
                logger.info(f'Writing {i}/{len(lines)} lines...')
            f.write(line + '\n')
            
            if line.startswith('#EXTINF'):
                try:
                    # Extract attributes using regex
                    xui_match = re.search(r'xui-id="([^"]*)"', line)
                    tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
                    tvg_name_match = re.search(r'tvg-name="([^"]*)"', line)
                    tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                    group_title_match = re.search(r'group-title="([^"]*)"', line)
                    
                    xui_id = xui_match.group(1) if xui_match else ''
                    tvg_id = tvg_id_match.group(1) if tvg_id_match else ''
                    tvg_name = tvg_name_match.group(1) if tvg_name_match else ''
                    tvg_logo = tvg_logo_match.group(1) if tvg_logo_match else ''
                    group_title = group_title_match.group(1) if group_title_match else ''
                    
                except Exception as e:
                    logger.error(f'Failed to parse EXTINF line: {line}: {e}')
                    continue
            elif line.strip() and not line.startswith('#'):
                # This is a URL line
                if line.endswith('m3u8'):
                    logger.info(f'Writing channel to database: {tvg_name}')
                    db.create('tv', {
                        'url': line,
                        'xui_id': xui_id,
                        'tvg_id': tvg_id,
                        'tvg_name': tvg_name,
                        'tvg_logo': tvg_logo,
                        'group_title': group_title,
                        'favorite': False
                    })
                else:
                    logger.warning(f'Line is not a live TV stream: {line}')

                # Reset attributes after processing URL
                xui_id = tvg_id = tvg_name = tvg_logo = group_title = ''

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

def favorite_channel(tvg_id: str):
    db.update(table='tv', data={'favorite': True}, params={'tvg_id': tvg_id})
    return Response.success('Channel favorited successfully')

def unfavorite_channel(tvg_id: str):
    db.update(table='tv', data={'favorite': False}, params={'tvg_id': tvg_id})
    return Response.success('Channel unfavorited successfully')
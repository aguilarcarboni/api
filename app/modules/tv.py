from app.helpers.logger import logger
from app.helpers.response import Response
import os
import requests

XTREAM_BASE_URL = "http://xdplayer.tv:8080"
XTREAM_USER = "aguilarcarboni"
XTREAM_PASS = "pXU2Hx6NMu"

def fetch_playlist():

    logger.info('Fetching playlist...')

    # Check if playlist file exists
    playlist_path = '/Users/andres/Documents/Repositories/Personal/laserfocus-api/cache/tv/playlist.m3u'

    if os.path.exists(playlist_path):
        logger.info('Reading playlist from cache...')
        with open(playlist_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.success('Playlist loaded from cache')
        return Response.success(content)

    # If file doesn't exist, fetch from API

    max_lines = 2000

    get_all_streams = f"/get.php?username={XTREAM_USER}&password={XTREAM_PASS}&type=m3u_plus&output=m3u8"
    response = requests.get(XTREAM_BASE_URL + get_all_streams)
    if response.status_code != 200:
        logger.error(f'Failed to fetch playlist: {response.status_code}')
        return Response.error(f'Failed to fetch playlist: {response.status_code}')
    logger.success('Playlist fetched successfully')

    # Save the first 2000 lines of the m3u file
    logger.info('Saving playlist...')
    with open(playlist_path, 'w', encoding='utf-8') as f:
        lines = response.text.splitlines()
        for i, line in enumerate(lines):
            if i % 100 == 0:
                logger.info(f'Writing {i}/{len(lines)} lines...')
            f.write(line + '\n')

    logger.announcement('Playlist saved successfully', 'success')
    return Response.success('Playlist saved successfully')

def get_channels():
    try:
        # Get channel list from Xtream API
        url = f"{XTREAM_BASE_URL}/player_api.php"
        params = {
            "username": XTREAM_USER,
            "password": XTREAM_PASS,
            "action": "get_live_streams"
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return Response.success(response.json())
        else:
            return Response.error("Failed to fetch channels")
    except Exception as e:
        return Response.error(str(e))
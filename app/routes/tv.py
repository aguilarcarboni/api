from flask import Blueprint
from app.modules.tv import get_channels, fetch_playlist
from app.helpers.exceptions import handle_exception

bp = Blueprint('tv', __name__)

"""
Get channel list from Xtream API
"""
@bp.route('/channels', methods=['GET'])
def get_channels_route():
    return get_channels()

"""
Fetch playlist from Xtream API
"""
@bp.route('/fetch_playlist', methods=['GET'])
def fetch_playlist_route():
    return fetch_playlist()
from flask import Blueprint, request
from src.components.tv import get_channels, fetch_channels_from_provider, favorite_channel, unfavorite_channel, create_credentials, get_credentials

bp = Blueprint('tv', __name__)

@bp.route('/channels/fetch', methods=['POST'])
def fetch_channels_from_provider_route():
    payload = request.get_json()
    return fetch_channels_from_provider(payload['user_id'])

@bp.route('/channels/list', methods=['GET'])
def get_channels_route():
    return get_channels()

@bp.route('/channels/favorite', methods=['POST'])
def favorite_channel_route():
    payload = request.get_json()
    return favorite_channel(payload['tvg_id'])

@bp.route('/channels/unfavorite', methods=['POST'])
def unfavorite_channel_route():
    payload = request.get_json()
    return unfavorite_channel(payload['tvg_id'])

@bp.route('/create-credentials', methods=['POST'])
def create_credentials_route():
    payload = request.get_json()
    return create_credentials(payload['user_id'], payload['url'], payload['username'], payload['password'])

@bp.route('/get-credentials', methods=['POST'])
def get_credentials_route():
    payload = request.get_json()
    return get_credentials(payload['user_id'])

from flask import jsonify, request
from app.api import bp
from app.services.xtreme_service import XtremeService

xtreme_service = XtremeService()

@bp.route('/authenticate', methods=['POST'])
def authenticate():
    data = xtreme_service.authenticate()
    return jsonify(data)

@bp.route('/live_streams', methods=['GET'])
def get_live_streams():
    data = xtreme_service.get_live_streams()
    return jsonify(data)

@bp.route('/vod_streams', methods=['GET'])
def get_vod_streams():
    data = xtreme_service.get_vod_streams()
    return jsonify(data)

@bp.route('/series', methods=['GET'])
def get_series():
    data = xtreme_service.get_series()
    return jsonify(data)

@bp.route('/epg', methods=['GET'])
def get_epg():
    stream_id = request.args.get('stream_id')
    data = xtreme_service.get_epg(stream_id)
    return jsonify(data)
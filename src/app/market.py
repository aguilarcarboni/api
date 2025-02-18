from flask import Blueprint, request
from src.components.market import get_historical_data, get_current_data

bp = Blueprint('market', __name__)

@bp.route("/historical", methods=['POST'])
def market_route():
    input_json = request.get_json(force=True)
    return get_historical_data(input_json['tickers'])

@bp.route("/current", methods=['POST'])
def current_route():
    input_json = request.get_json(force=True)
    return get_current_data(input_json['ticker'])
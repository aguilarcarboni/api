from flask import Blueprint, request
from src.components.market import get_historical_data

bp = Blueprint('market', __name__)

@bp.route("/historical", methods=['POST'])
def market_route():
    input_json = request.get_json(force=True)
    return get_historical_data(input_json['tickers'])
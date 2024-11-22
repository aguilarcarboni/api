from flask import Blueprint, request
from src.components.market import getHistoricalData

bp = Blueprint('market', __name__)

@bp.route("/historical", methods=['POST'])
def market_route():
    input_json = request.get_json(force=True)
    return getHistoricalData(input_json['tickers'])

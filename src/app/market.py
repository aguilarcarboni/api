from flask import Blueprint, request
from src.components.market import historical_stock_price, latest_stock_price

bp = Blueprint('market', __name__) 

@bp.route('/latest-price/stock', methods=['POST'])
def latest_price_route():
    payload = request.get_json(force=True)
    symbol = payload.get('symbol', None)
    return latest_stock_price(symbol)

@bp.route('/historical-price/stock', methods=['POST'])
def historical_price_route():
    payload = request.get_json(force=True)
    symbol = payload.get('symbol', None)
    period = payload.get('period', None)
    return historical_stock_price(symbol, period)
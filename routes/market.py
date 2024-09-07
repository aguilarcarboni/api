from flask import Blueprint, jsonify
from laserfocus import Market

bp = Blueprint('market', __name__)

Market = Market()

@bp.route("/market")
def market():
    marketData = {
        'stocks':{
            'historical': Market.getMarketData()
        },
    }

    return marketData

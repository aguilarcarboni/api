from flask import Blueprint, jsonify
import laserfocus

bp = Blueprint('market', __name__)

@bp.route("/market")
def market():
    marketData = {
        'stocks':{
            'historical': laserfocus.Market.getMarketData()
        },
    }

    return marketData

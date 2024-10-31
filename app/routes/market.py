from flask import Blueprint
from app.modules.market import getMarketData

bp = Blueprint('market', __name__)

@bp.route("/")
def market_route():
    marketData = {
        'stocks':{
            'historical': getMarketData()
        },
    }

    return marketData

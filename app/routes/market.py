from flask import Blueprint
from app.modules.market import getMarketData

bp = Blueprint('market', __name__)

@bp.route("/market")
def market():
    marketData = {
        'stocks':{
            'historical': getMarketData()
        },
    }

    return marketData

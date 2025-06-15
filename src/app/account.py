from flask import Blueprint
from src.components.account import summary, positions, portfolio, pnl, pnl_single

bp = Blueprint('account', __name__) 

@bp.route('/summary', methods=['GET'])
def summary_route():
    return summary()

@bp.route('/positions', methods=['GET'])
def positions_route():  
    return positions()

@bp.route('/portfolio', methods=['GET'])
def portfolio_route():
    return portfolio()

@bp.route('/pnl', methods=['GET'])
def pnl_route():
    return pnl()

@bp.route('/pnl-single', methods=['GET'])
def pnl_single_route():
    return pnl_single()
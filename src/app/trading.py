from flask import Blueprint
from src.components.trading import get_account_summary

bp = Blueprint('trading', __name__)

@bp.route('/account/summary', methods=['POST'])
def get_account_summary_route():
    return get_account_summary()
from flask import Blueprint
from src.utils.connectors.ibkr import IBKRConnector

bp = Blueprint('trading', __name__)

connector = IBKRConnector()

@bp.route('/account/summary', methods=['POST'])
def get_account_summary_route():
    return connector.get_account_summary()
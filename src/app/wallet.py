from flask import Blueprint, request

from src.components.wallet.components.bac import db, generateStatements

bp = Blueprint('wallet', __name__)

@bp.route("/bac/accounts", methods=['POST'])
def bac_accounts_route():
    return db.read('account')

@bp.route("/bac/expenses", methods=['POST'])
def bac_expenses_route():
    payload = request.get_json(force=True)
    params = payload['params']
    return db.read('expense', params)

@bp.route("/bac/generate_statements", methods=['POST'])
def bac_generate_statements_route():
    payload = request.get_json(force=True)
    account = payload['account']
    month = payload['month']
    return generateStatements(account, month)
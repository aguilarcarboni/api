from flask import Blueprint, request

from src.components.wallet.components.bac import db, generateStatements

bp = Blueprint('wallet', __name__)

@bp.route("/accounts", methods=['POST'])
def accounts_route():
    return db.read('account')

@bp.route("/expenses", methods=['POST'])
def expenses_route():
    payload = request.get_json(force=True)
    params = payload['params']
    return db.read('expense', params)

@bp.route("/generate_statements", methods=['POST'])
def generate_statements_route():
    payload = request.get_json(force=True)
    account = payload['account']
    month = payload['month']
    return generateStatements(account, month)

@bp.route("/budget", methods=['POST'])
def budget_route():
    return db.read('category')
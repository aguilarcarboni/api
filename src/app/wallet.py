from flask import Blueprint, request

from src.components.wallet.statements.sources.bac import db, generateStatements

bp = Blueprint('wallet', __name__)

@bp.route("/bac/expenses", methods=['POST'])
def bac_expenses_route():
    payload = request.get_json(force=True)
    params = payload['params']
    return db.read('expense', params)

@bp.route("/bac/generate_statements", methods=['POST'])
def bac_generate_statements_route():
    payload = request.get_json(force=True)
    account = payload['account']
    file_name = payload['file_name']
    return generateStatements(account, file_name)
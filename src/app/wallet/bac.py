from flask import Blueprint, request

from src.components.wallet.bac import BAC, read

bp = Blueprint('bac', __name__)

BAC = BAC()

@bp.route("/expenses", methods=['POST'])
def bac_expenses_route():
    payload = request.get_json(force=True)
    params = payload['params']
    return read('expense', params)

@bp.route("/generate_statements", methods=['POST'])
def bac_generate_statements_route():
    payload = request.get_json(force=True)
    account = payload['account']
    file_name = payload['file_name']
    return BAC.generateStatements(account, file_name)
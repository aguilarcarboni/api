from flask import Blueprint, request
from app.modules.wallet.bac import BAC, read
from app.helpers.logger import logger

bp = Blueprint('bac', __name__)

BAC = BAC()

@bp.route("/expenses", methods=['POST'])
def bac_expenses_route():
    payload = request.get_json(force=True)
    params = payload['params']
    response = read('expense', params)
    return response

@bp.route("/generate_statements", methods=['POST'])
def bac_generate_statements_route():
    payload = request.get_json(force=True)
    account = payload['account']
    file_name = payload['file_name']
    response = BAC.generateStatements(account, file_name)
    return response
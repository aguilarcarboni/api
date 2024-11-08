from flask import Blueprint, request
from app.modules.wallet import BAC, IBKR

bp = Blueprint('wallet', __name__)

BAC = BAC()
IBKR = IBKR()

@bp.route("/generate_statements", methods=['POST'])
def bac_generate_statements_route():

    input_json = request.get_json(force=True)

    account = input_json['account']
    file_name = input_json['file_name']

    response = BAC.generateStatements(account, file_name)
    return response
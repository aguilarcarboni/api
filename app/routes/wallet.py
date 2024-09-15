from flask import Blueprint, request
from app.modules.wallet import BAC

bp = Blueprint('wallet', __name__)

BAC = BAC()

@bp.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    input_json = request.get_json(force=True)

    account = input_json['account']
    file_name = input_json['file_name']

    response = BAC.generateStatements(account, file_name)
    return response
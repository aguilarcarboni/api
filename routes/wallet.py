from flask import Blueprint, request
from laserfocus import Wallet

bp = Blueprint('wallet', __name__)

Wallet = Wallet()

@bp.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    # Is document given?

    BAC = Wallet.BAC()

    # Query drive for document
    input_json = request.get_json(force=True)

    # Acccccc
    account = input_json['account']
    file_name = input_json['file_name']

    response = BAC.generateStatements(account, file_name)
    return response
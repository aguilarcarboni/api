from flask import Blueprint, request
from app.modules.database import create, read, update, delete

bp = Blueprint('database', __name__)

@bp.route('/database/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    response = create(table_name=payload['table'], data=payload['data'])
    return response

@bp.route('/database/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    response = read(table=payload['table'], params=payload['params'])
    return response

@bp.route('/database/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    response = update(table_name=payload['table'], params=payload['query'], data=payload['data'])
    return response

@bp.route('/database/delete', methods=['POST'])
def delete_user_route():
    payload = request.get_json(force=True)
    response = delete(table=payload['table'], params=payload['params'])
    return response
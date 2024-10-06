from flask import Blueprint, request
from app.modules.database import create, read, update, delete, get_foreign_keys, get_parent_lineage

bp = Blueprint('database', __name__)

@bp.route('/database/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    response = create(table=payload['table'], data=payload['data'])
    return response

@bp.route('/database/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    if isinstance(payload, str):
        import json
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON string"}, 400
    response = read(table=payload['table'], params=payload['params'])
    return response

@bp.route('/database/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    response = update(table=payload['table'], params=payload['params'], data=payload['data'])
    return response

@bp.route('/database/delete', methods=['POST'])
def delete_user_route():
    payload = request.get_json(force=True)
    response = delete(table=payload['table'], params=payload['params'])
    return response

@bp.route('/database/get_foreign_keys', methods=['POST'])
def get_foreign_keys_route():
    payload = request.get_json(force=True)
    response = get_foreign_keys(table=payload['table'], params=payload['params'])
    return response

@bp.route('/database/get_parent_lineage', methods=['POST'])
def get_parent_lineage_route():
    payload = request.get_json(force=True)
    if 'depth' not in payload:
        payload['depth'] = 3
    elif payload['depth'] > 10:
        payload['depth'] = 10
    response = get_parent_lineage(table=payload['table'], params=payload['params'], depth=payload['depth'])
    return response
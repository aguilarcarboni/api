from flask import request, Blueprint
from src.components.user import db

bp = Blueprint('user', __name__)

@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return db.create(table='user', data=payload['data'])

@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return db.read(table='user', params=payload['params'])

@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return db.update(table='user', params=payload['params'], data=payload['data'])

@bp.route('/delete', methods=['POST'])
def delete_route():
    payload = request.get_json(force=True)
    return db.delete(table='user', params=payload['params'])
from flask import request, Blueprint
from src.components.laserfocus import db

bp = Blueprint('project', __name__)

@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return db.create(table='project', data=payload['data'])

@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return db.read(table='project', params=payload['params'])

@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return db.update(table='project', params=payload['params'], data=payload['data'])

@bp.route('/delete', methods=['POST'])
def delete_route():
    payload = request.get_json(force=True)
    return db.delete(table='project', params=payload['params'])
from flask import request, Blueprint
from src.components.laserfocus import LaserFocus

bp = Blueprint('space', __name__)

laserfocus = LaserFocus()
db = laserfocus.db

@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return db.create(table='space', data=payload['data'])

@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return db.read(table='space', params=payload['params'])

@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return db.update(table='space', params=payload['params'], data=payload['data'])

@bp.route('/delete', methods=['POST'])
def delete_route():
    payload = request.get_json(force=True)
    return db.delete(table='space', params=payload['params'])
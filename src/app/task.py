from flask import request, Blueprint
from src.components.laserfocus import LaserFocus

bp = Blueprint('task', __name__)

laserfocus = LaserFocus()
db = laserfocus.db

@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return db.create(table='task', data=payload['data'])

@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return db.read(table='task', params=payload['params'])

@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return db.update(table='task', params=payload['params'], data=payload['data'])

@bp.route('/delete', methods=['POST'])
def delete_route():
    payload = request.get_json(force=True)
    return db.delete(table='task', params=payload['params'])

@bp.route('/create-link', methods=['POST'])
def create_link_route():
    payload = request.get_json(force=True)
    return db.create(table='task_link', data=payload['data'])

@bp.route('/read-links', methods=['POST'])
def read_links_route():
    payload = request.get_json(force=True)
    return db.read(table='task_link', params=payload['params'])
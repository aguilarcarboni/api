from flask import request, Blueprint
from src.components.lists import db

bp = Blueprint('lists', __name__)

@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return db.create(table=payload['table'], data=payload['data'])

@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return db.read(table=payload['table'], params=payload['params'])

@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return db.update(table=payload['table'], params=payload['params'], data=payload['data'])

@bp.route('/delete', methods=['POST'])
def delete_route():
    payload = request.get_json(force=True)
    return db.delete(table=payload['table'], params=payload['params'])

@bp.route('/tables', methods=['GET'])
def get_tables_route():
    return db.get_tables()

@bp.route('/schema', methods=['POST'])
def get_schema_route():
    payload = request.get_json(force=True)
    return db.get_schema(table=payload['table'])
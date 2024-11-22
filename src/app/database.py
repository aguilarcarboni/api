from flask import Blueprint, request
from src.components.database import create, read, update, delete, get_parent_lineage

bp = Blueprint('database', __name__)

"""
Create a new record in the database

Payload:
    table: str
    data: dict
"""
@bp.route('/create', methods=['POST'])
def create_route():
    payload = request.get_json(force=True)
    return create(table=payload['table'], data=payload['data'])


"""
Read records from the database

Payload:
    table: str
    params: dict
"""
@bp.route('/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    return read(table=payload['table'], params=payload['params'])

"""
Update a record in the database

Payload:
    table: str
    params: dict
    data: dict
"""
@bp.route('/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    return update(table=payload['table'], params=payload['params'], data=payload['data'])

"""
Delete a record from the database

Payload:
    table: str
    params: dict
"""
@bp.route('/delete', methods=['POST'])
def delete_user_route():
    payload = request.get_json(force=True)
    return delete(table=payload['table'], params=payload['params'])

"""
Get the parent lineage of a record

Payload:
    table: str
    params: dict
"""
@bp.route('/get_parent_lineage', methods=['POST'])
def get_parent_lineage_route():
    payload = request.get_json(force=True)
    
    response = get_parent_lineage(
        table=payload['table'], 
        params=payload['params'], 
        depth=3
    )

    return response
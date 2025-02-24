from flask import request, Blueprint
from src.components.wallet.wallet import db as wallet_db
from src.utils.response import Response

bp = Blueprint('databases', __name__)

# Dictionary of available public databases
databases = {
    'wallet': wallet_db,
}

@bp.route('/list', methods=['GET'])
def get_databases_route():
    return Response.success(list(databases.keys()))

@bp.route('/<database>/create', methods=['POST'])
def create_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].create(table=payload['table'], data=payload['data'])

@bp.route('/<database>/read', methods=['POST'])
def read_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].read(table=payload['table'], params=payload['params'])

@bp.route('/<database>/update', methods=['POST'])
def update_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].update(table=payload['table'], params=payload['params'], data=payload['data'])

@bp.route('/<database>/delete', methods=['POST'])
def delete_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].delete(table=payload['table'], params=payload['params'])

@bp.route('/<database>/tables', methods=['GET'])
def get_tables_route(database):
    if database not in databases:
        return Response.error('Database not found')
    return databases[database].get_tables()

@bp.route('/<database>/schema', methods=['POST'])
def get_schema_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].get_schema(table=payload['table'])

@bp.route('/<database>/from_data_object', methods=['POST'])
def from_data_object_route(database):
    if database not in databases:
        return Response.error('Database not found')
    payload = request.get_json(force=True)
    return databases[database].from_data_object(data=payload['data'], table=payload['table'], overwrite=payload['overwrite'])
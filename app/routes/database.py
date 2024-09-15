from flask import Blueprint, request
from app.modules.database import create, UserPayload, SpacePayload, EventPayload, read, delete

bp = Blueprint('database', __name__)

@bp.route('/database/create', methods=['POST'])
def create_route():

    payload = request.get_json(force=True)
    if (payload['table'] == 'User'):
        data = UserPayload(**payload['data'])
    elif (payload['table'] == 'Space'):
        data = SpacePayload(**payload['data'])
    elif (payload['table'] == 'Event'):
        data = EventPayload(**payload['data'])
    else:
        raise ValueError(f"Invalid table {payload['table']}")

    response = create(data.to_orm())
    return response

@bp.route('/database/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    response = read(payload['table'], payload['query'])
    return response

@bp.route('/database/delete', methods=['POST'])
def delete_user_route():
    payload = request.get_json(force=True)
    response = delete(payload['table'], payload['query'])
    return response
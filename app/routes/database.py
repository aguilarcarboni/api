from flask import Blueprint, request
from app.modules.database import create, read, update, delete, UserPayload, SpacePayload, EventPayload, PagePayload

bp = Blueprint('database', __name__)

@bp.route('/database/create', methods=['POST'])
def create_route():

    payload = request.get_json(force=True)

    response = create(payload['table'], payload['data'])
    return response

@bp.route('/database/read', methods=['POST'])
def read_route():
    payload = request.get_json(force=True)
    response = read(payload['table'], payload['query'])
    return response

@bp.route('/database/update', methods=['POST'])
def update_route():
    payload = request.get_json(force=True)
    response = update(payload['table'], payload['query'], payload['data'])
    return response

@bp.route('/database/delete', methods=['POST'])
def delete_user_route():
    payload = request.get_json(force=True)
    response = delete(payload['table'], payload['query'])
    return response
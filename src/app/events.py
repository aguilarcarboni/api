from flask import Blueprint, request
from src.components.events import create_event, read_events, update_event, delete_event
from laserfocus.utils.managers.scopes import verify_scope

bp = Blueprint('events', __name__)

@bp.route('/create', methods=['POST'])
@verify_scope('event/create')
def create_event_route():
    payload = request.get_json(force=True)
    event = payload.get('event', None)
    return create_event(event=event)

@bp.route('/read', methods=['POST'])
@verify_scope('event/read')
def read_events_route():
    payload = request.get_json(force=True)
    query = payload.get('query', None)
    return read_events(query=query)

@bp.route('/update', methods=['POST'])
@verify_scope('event/update')
def update_event_route():
    payload = request.get_json(force=True)
    event = payload.get('event', None)
    query = payload.get('query', None)
    return update_event(query=query, event=event)

@bp.route('/delete', methods=['POST'])
@verify_scope('event/delete')
def delete_event_route():
    payload = request.get_json(force=True)
    query = payload.get('query', None)
    return delete_event(query=query)
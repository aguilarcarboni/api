from laserfocus.utils.exception import handle_exception
from laserfocus.utils.logger import logger

from src.utils.connectors.sqlite import db

logger.announcement('Initializing Event Service', type='info')
logger.announcement('Initialized Event Service', type='success')
    
@handle_exception
def create_event(event: dict = None):
    event_id = db.create(table='event', data=event)
    return {'id': event_id}

@handle_exception
def read_events(query: dict = None):
    events = db.read(table='event', query=query)
    return events

@handle_exception
def update_event(query: dict = None, event: dict = None):
    event_id = db.update(table='event', query=query, data=event)
    return {'id': event_id}

@handle_exception
def delete_event(query: dict = None):
    event_id = db.delete(table='event', query=query)
    return {'id': event_id}
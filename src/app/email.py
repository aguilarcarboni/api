from flask import Blueprint, request
from src.components.email import Gmail

bp = Blueprint('email', __name__)

Email = Gmail()

@bp.route('/send_email', methods=['POST'])
def send_email_route():
    payload = request.get_json(force=True)
    
    plain_text = payload['plain_text']
    to_email = payload['to_email']
    subject = payload['subject']

    response = Email.send_email(plain_text, to_email, subject)
    return response

@bp.route('/get_thread', methods=['POST'])
def get_thread_route():
    payload = request.get_json(force=True)
    thread_id = payload['thread_id']
    response = Email.get_thread(thread_id)
    return response


@bp.route('/list_threads', methods=['POST'])
def list_threads_route():
    payload = request.get_json(force=True)
    query = payload['query']
    max_results = payload['max_results']
    response = Email.list_threads(query, max_results)
    return response

@bp.route('/modify_labels', methods=['POST'])
def modify_labels_route():
    payload = request.get_json(force=True)
    message_id = payload['message_id']
    add_labels = payload['add_labels']
    remove_labels = payload['remove_labels']
    response = Email.modify_labels(message_id, add_labels, remove_labels)
    return response


@bp.route('/get_message', methods=['POST'])
def get_message_route():
    payload = request.get_json(force=True)
    message_id = payload['message_id']
    response = Email.get_message(message_id)
    return response

@bp.route('/fetch_detailed_emails', methods=['POST'])
def fetch_detailed_emails_route():
    payload = request.get_json(force=True)
    query = payload.get('query', None)
    max_results = payload.get('max_results', 10)
    response = Email.fetch_detailed_emails(query, max_results)
    return response

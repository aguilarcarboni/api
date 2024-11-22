from flask import Blueprint, request

from src.components.email import Gmail

bp = Blueprint('email', __name__)

Email = Gmail()

@bp.route('/send', methods=['POST'])
def send_route():
    payload = request.get_json(force=True)
    
    plain_text = payload['plain_text']
    to_email = payload['to_email']
    subject = payload['subject']

    response = Email.sendEmail(plain_text, to_email, subject)
    return response
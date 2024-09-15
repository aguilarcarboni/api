from flask import Blueprint, jsonify
from app.modules.date_and_time import getCurrentDate, getCurrentTime

bp = Blueprint('main', __name__)

@bp.route("/")
def root():
    data = {
        'title': 'any path to success starts with laserfocus.',
        'date': getCurrentDate(),
        'time': getCurrentTime(),
    }
    return jsonify(data)
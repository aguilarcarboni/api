from flask import Blueprint, jsonify
from laserfocus import DateAndTime

bp = Blueprint('main', __name__)

DateAndTime = DateAndTime()

@bp.route("/")
def root():
    data = {
        'title': 'any path to success starts with laserfocus.',
        'date': DateAndTime.currentDate,
        'time': DateAndTime.currentTime,
    }
    return jsonify(data)
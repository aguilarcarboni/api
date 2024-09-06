from flask import Blueprint, jsonify
import laserfocus

bp = Blueprint('main', __name__)

@bp.route("/")
def root():
    data = {
        'title': 'any path to success starts with laserfocus.',
        'date': laserfocus.DateAndTime.currentDate,
        'time': laserfocus.DateAndTime.currentTime,
    }
    return jsonify(data)
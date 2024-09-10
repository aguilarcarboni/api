from functools import wraps
from flask import jsonify
import requests

def handle_api_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500
    return decorated_function
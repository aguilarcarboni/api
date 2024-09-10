from flask import Blueprint

bp = Blueprint('sports', __name__)

@bp.route("/sports")
def sports():
    sportsData = {}
    return sportsData

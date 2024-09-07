from flask import Blueprint
from laserfocus import Explorer

bp = Blueprint('explorer', __name__)

Explorer = Explorer()

@bp.route("/explorer/mars")
def mars():
    marsData = Explorer.Mars.data
    return marsData

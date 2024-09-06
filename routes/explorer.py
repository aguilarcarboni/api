from flask import Blueprint
import laserfocus

bp = Blueprint('explorer', __name__)

@bp.route("/explorer/mars")
def mars():
    marsData = laserfocus.Explorer.Mars.data
    return marsData

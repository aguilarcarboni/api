from flask import Blueprint
from app.modules.explorer import Mars

bp = Blueprint('explorer', __name__)



@bp.route("/explorer/mars")
def mars():
    marsData = Mars.data
    return marsData

from flask import Blueprint
from app.modules.explorer import Mars

bp = Blueprint('explorer', __name__)

@bp.route("/mars")
def mars_route():
    marsData = Mars.data
    return marsData

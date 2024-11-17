from flask import Blueprint
from app.helpers.response import Response
bp = Blueprint('spotify', __name__)

@bp.route('/')
def index():
    return Response.success('Spotify API')
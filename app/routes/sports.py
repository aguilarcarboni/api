from flask import Blueprint
from app.modules.sports import ESPN

bp = Blueprint('sports', __name__)

ESPN = ESPN()

@bp.route("/get_nfl_scoreboard", methods=['GET'])
def get_nfl_scoreboard_route():
    return ESPN.get_nfl_scoreboard()

@bp.route("/get_nba_scoreboard", methods=['GET'])
def get_nba_scoreboard_route():
    return ESPN.get_nba_scoreboard()

@bp.route("/get_nba_news", methods=['GET'])
def get_nba_news_route():
    return ESPN.get_nba_news()

@bp.route("/get_nfl_news", methods=['GET'])
def get_nfl_news_route():
    return ESPN.get_nfl_news()

@bp.route("/get_scoreboard", methods=['GET'])
def get_scoreboard_route():
    return ESPN.get_scoreboard()
    
from flask import Blueprint
from app.modules.news import scrapeCNNHeadlines

bp = Blueprint('news', __name__)

@bp.route("/")
def news_route():
    newsData = scrapeCNNHeadlines()
    return newsData
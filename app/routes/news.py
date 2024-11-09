from flask import Blueprint
from app.modules.news import NewsAggregator

bp = Blueprint('news', __name__)

aggregator = NewsAggregator()

@bp.route("/personalized")
def get_personalized_news_route():
    return aggregator.get_personalized_news()

@bp.route("/fetch")
def fetch_news_route():
    return aggregator.fetch_news()

from flask import Blueprint, request
from app.modules.news import NewsAggregator

bp = Blueprint('news', __name__)

aggregator = NewsAggregator()

@bp.route("/get_personalized_news", methods=['GET'])
def get_personalized_news_route():
    return aggregator.get_personalized_news()

@bp.route("/fetch_news", methods=['GET'])
def fetch_news_route():
    return aggregator.fetch_news()

@bp.route("/add_interest", methods=['POST'])
def add_interest_route():
    payload = request.get_json()
    interest = payload['interest']
    keywords = payload['keywords']
    return aggregator.add_interest(interest, keywords)

@bp.route("/get_interests", methods=['GET'])
def get_interests_route():
    return aggregator.get_interests()
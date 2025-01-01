from flask import Blueprint, request
from src.components.news.news import get_personalized_news, fetch_news, add_interest, get_interests

bp = Blueprint('news', __name__)

@bp.route("/get_personalized_news", methods=['GET'])
def get_personalized_news_route():
    return get_personalized_news()

@bp.route("/fetch_news", methods=['GET'])
def fetch_news_route():
    return fetch_news()

@bp.route("/add_interest", methods=['POST'])
def add_interest_route():
    payload = request.get_json()
    interest = payload['interest']
    keywords = payload['keywords']
    return add_interest(interest, keywords)

@bp.route("/get_interests", methods=['GET'])
def get_interests_route():
    return get_interests()
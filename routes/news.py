from flask import Blueprint
from laserfocus import News

bp = Blueprint('news', __name__)

News = News()

@bp.route("/news")
def news():
    newsData = News.scrapeCNNHeadlines()
    return newsData
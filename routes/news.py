from flask import Blueprint
import laserfocus

bp = Blueprint('news', __name__)

@bp.route("/news")
def news():
    newsData = laserfocus.News.scrapeCNNHeadlines()
    return newsData
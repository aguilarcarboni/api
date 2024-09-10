from flask import Blueprint
from laserfocus import Weather

bp = Blueprint('weather', __name__)

Weather = Weather('9', '-84')

@bp.route("/weather")
def weather():
    weatherData = {
        'forecast': Weather.forecast, 
        'currentWeather': Weather.currentWeather,
    }
    return weatherData
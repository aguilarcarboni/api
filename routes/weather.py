from flask import Blueprint
import laserfocus

bp = Blueprint('weather', __name__)

@bp.route("/weather")
def weather():
    weatherData = {
        'forecast':laserfocus.Weather.forecast, 
        'currentWeather': laserfocus.Weather.currentWeather,
    }
    return weatherData
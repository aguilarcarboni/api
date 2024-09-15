from flask import Blueprint
from app.modules.weather import getHourlyFourDayForecast, getCurrentWeather

bp = Blueprint('weather', __name__)

@bp.route("/weather")
def weather():
    weatherData = {
        'forecast': getHourlyFourDayForecast(), 
        'currentWeather': getCurrentWeather(),
    }
    return weatherData
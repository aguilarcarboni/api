from app.helpers.logger import logger
from app.modules.location import location

import openmeteo_requests
import requests_cache
from retry_requests import retry

import pandas as pd


def connectToOpenMeteo(lat,lon):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "is_day", "rain", "showers", "weather_code"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "rain", "showers", "weather_code", "visibility", "uv_index", "uv_index_clear_sky", "is_day"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "rain_sum", "showers_sum", "precipitation_hours"],
        "timezone": "America/Denver",
        "forecast_days": 3
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses[0]

def getCurrentWeather():
    # Current values. The order of variables needs to be the same as requested.
    current = service.Current()
    data = {
        'temperature':current.Variables(0).Value(),
        'humidity':current.Variables(1).Value(),
        'is_day':current.Variables(2).Value(),
        'rain':current.Variables(3).Value(),
        'showers':current.Variables(4).Value(),
        'weather_code':current.Variables(5).Value()
    }
    return data

def getHourlyFourDayForecast():
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = service.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_showers = hourly.Variables(4).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(6).ValuesAsNumpy()
    hourly_uv_index = hourly.Variables(7).ValuesAsNumpy()
    hourly_uv_index_clear_sky = hourly.Variables(8).ValuesAsNumpy()
    hourly_is_day = hourly.Variables(9).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature"] = hourly_temperature_2m
    hourly_data["humidity"] = hourly_relative_humidity_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["rain"] = hourly_rain
    hourly_data["showers"] = hourly_showers
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["visibility"] = hourly_visibility
    hourly_data["uv_index"] = hourly_uv_index
    hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
    hourly_data["is_day"] = hourly_is_day

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    data = hourly_dataframe.to_dict(orient="records")
    return data


logger.info(f"Initializing Weather for lat: {location.coordinates['lat']}, lon: {location.coordinates['lon']}.")
service = connectToOpenMeteo(location.coordinates['lat'], location.coordinates['lon'])
logger.success("Successfully initialized Weather.")

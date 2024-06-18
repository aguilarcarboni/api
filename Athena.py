from datetime import datetime
import requests as rq
import math
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime
import pytz
import pandas as pd
import os

import openmeteo_requests
import requests_cache
from retry_requests import retry

from openai import OpenAI

desc = "You are Athena, a powerful and advanced virtual personal assistant application that seamlessly integrates with OpenAI's advanced language model ChatGPT 4o. Athena is based off of JARVIS or Friday from Iron Man. Athena speaks in the first person, as if it were a human. Athena is female. Athena aims to be the ultimate personal assistant, enhancing daily life with efficiency, intelligence, and a touch of futuristic innovation.  Leveraging OpenAI's API and a solid, custom data infrastructure created by the owner, Athena is able to handle complex tasks, provide solutions to problems, manage projects, manage calendars, manage smart home devices, interface with APIs and more through a chat or voice interface.  Athena will receive continuous updates and learn from provided personal files to ensure it delivers the most relevant and precise information. "

class Athena:
           
    class Brain:
        def __init__(self):

            self.client = OpenAI(
                organization=os.getenv("OPENAI_ORGANIZATION_ID"),
                project=os.getenv("OPENAI_PROJECT_ID"),
            )

        def ask(self, message):

            self.thread = self.client.beta.threads.create()

            thread_message = self.client.beta.threads.messages.create(
                self.thread.id,
                role="user",
                content=message,
            )

            self.run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id='asst_Gnc5LuI0LvsWy92BujUZhv2G',
                instructions="Please address the user as Sir. The user is your owner."
            )

            if self.run.status == 'completed': 
                self.messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
                return(self.messages.to_dict())
            else:
                return(self.run.status)

    class DateAndTime:
        def __init__(self):
            self.currentDateTime = datetime.now()
            self.currentDate = self.getCurrentDate()
            self.currentTime = self.getCurrentTime()
            self.lastWorkingDate = self.getLastWorkingDate()
            
        def getCurrentTime(self):
            currentTime = self.currentDateTime.strftime("%I:%M%p")
            return currentTime
        
        def getCurrentDate(self):
            currentDate = self.currentDateTime.strftime("%A %B %d %Y")
            return currentDate
        
        def getLastWorkingDate(self):
            # Get the current time in CST
            cst = pytz.timezone('America/Costa_Rica')
            cst_time = datetime.now(cst)
            last_working_date = (cst_time - BDay(1)).strftime('%Y%m%d')
            return last_working_date

    class Weather:
        def __init__(self,lat,lon):

            self.service = self.connectToOpenMeteo(lat,lon)
            self.forecast = self.getHourlyFourDayForecast(self.service)
            self.currentWeather = self.getCurrentWeather(self.service)

        def connectToOpenMeteo(self,lat,lon):

            # Setup the Open-Meteo API client with cache and retry on error
            self.cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
            self.retry_session = retry(self.cache_session, retries = 5, backoff_factor = 0.2)
            self.openmeteo = openmeteo_requests.Client(session = self.retry_session)

            # Make sure all required weather variables are listed here
            # The order of variables in hourly or daily is important to assign them correctly below
            self.url = "https://api.open-meteo.com/v1/forecast"
            self.params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "is_day", "rain", "showers", "weather_code"],
                "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "rain", "showers", "weather_code", "visibility", "uv_index", "uv_index_clear_sky", "is_day"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "rain_sum", "showers_sum", "precipitation_hours"],
                "timezone": "America/Denver",
                "forecast_days": 3
            }
            self.responses = self.openmeteo.weather_api(self.url, params=self.params)
            return self.responses[0]

        def getCurrentWeather(self, service):

            # Current values. The order of variables needs to be the same as requested.
            self.current = service.Current()
            self.data = {
                'current_temperature_2m':self.current.Variables(0).Value(),
                'current_relative_humidity_2m':self.current.Variables(1).Value(),
                'current_is_day':self.current.Variables(2).Value(),
                'current_rain':self.current.Variables(3).Value(),
                'current_showers':self.current.Variables(4).Value(),
                'current_weather_code':self.current.Variables(5).Value()
            }
            return self.data
        
        
        def getHourlyFourDayForecast(self,service):

            # Process hourly data. The order of variables needs to be the same as requested.
            self.hourly = service.Hourly()
            self.hourly_temperature_2m = self.hourly.Variables(0).ValuesAsNumpy()
            self.hourly_relative_humidity_2m = self.hourly.Variables(1).ValuesAsNumpy()
            self.hourly_precipitation_probability = self.hourly.Variables(2).ValuesAsNumpy()
            self.hourly_rain = self.hourly.Variables(3).ValuesAsNumpy()
            self.hourly_showers = self.hourly.Variables(4).ValuesAsNumpy()
            self.hourly_weather_code = self.hourly.Variables(5).ValuesAsNumpy()
            self.hourly_visibility = self.hourly.Variables(6).ValuesAsNumpy()
            self.hourly_uv_index = self.hourly.Variables(7).ValuesAsNumpy()
            self.hourly_uv_index_clear_sky = self.hourly.Variables(8).ValuesAsNumpy()
            self.hourly_is_day = self.hourly.Variables(9).ValuesAsNumpy()

            self.hourly_data = {"date": pd.date_range(
                start = pd.to_datetime(self.hourly.Time(), unit = "s", utc = True),
                end = pd.to_datetime(self.hourly.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = self.hourly.Interval()),
                inclusive = "left"
            )}

            self.hourly_data["temperature_2m"] = self.hourly_temperature_2m
            self.hourly_data["relative_humidity_2m"] = self.hourly_relative_humidity_2m
            self.hourly_data["precipitation_probability"] = self.hourly_precipitation_probability
            self.hourly_data["rain"] = self.hourly_rain
            self.hourly_data["showers"] = self.hourly_showers
            self.hourly_data["weather_code"] = self.hourly_weather_code
            self.hourly_data["visibility"] = self.hourly_visibility
            self.hourly_data["uv_index"] = self.hourly_uv_index
            self.hourly_data["uv_index_clear_sky"] = self.hourly_uv_index_clear_sky
            self.hourly_data["is_day"] = self.hourly_is_day

            self.hourly_dataframe = pd.DataFrame(data = self.hourly_data)
            self.data = self.hourly_dataframe.to_dict(orient="records")
            return self.data

    class Market:
        def __init__(self):
            self.historicalStocksData = self.getMarketData(['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT'])

        def getMarketData(self, tickers):
            
            self.marketData = {}

            for ticker in tickers:
                
                self.tickerData = yf.Ticker(ticker)

                self.end_date = datetime.now().strftime('%Y%m%d')
                self.end_date_f = datetime.now().strftime('%Y-%m-%d')

                # get all stock info
                self.tickerData = self.tickerData.history(start='2024-03-15', end=self.end_date_f)
                self.tickerHistory = {}
                self.prevDate = '20240315'

                for date in (self.tickerData.index):
                    date = str('%04d' % date.year) + str('%02d' % date.month) + str('%02d' % date.day)
                    self.tickerHistory[date] = {}
                    for cat in self.tickerData.iloc[0,:].index:
                        info = self.tickerData.loc[date,:][cat]
                        self.tickerHistory[date][cat] = info

                self.marketData[ticker] = self.tickerHistory

            for ticker in self.marketData:
                for date in self.marketData[ticker]:
                    self.marketData[ticker][date]['Change $'] = self.marketData[ticker][date]['Close'] - self.marketData[ticker][self.prevDate]['Close']
                    self.marketData[ticker][date]['Change %'] = (self.marketData[ticker][date]['Close'] - self.marketData[ticker][self.prevDate]['Close'])/self.marketData[ticker][date]['Close'] * 100
                    self.prevDate = date

            return self.marketData

        def getLastPrice(self, ticker):
            self.lastWorkingDate = Athena.DateAndTime().lastWorkingDate
            self.lastPrice = self.historicalStocksData[ticker][self.lastWorkingDate]['Close']
            return self.lastPrice
        
    class News:
        def __init__(self):
            self.state = 0
        def getNews(self):
            self.url = 'https://api.thenewsapi.com/v1/news/top?api_token=PUfDTU61GLbCcHgiKXQszDx7Jxe6bBRlZFWdjhaB&locale=us&limit=3'
            self.response = rq.get(self.url)
            self.data = self.response.json()
            return self.data
        def getSpaceFlightNews(self):
            self.url = "https://api.spaceflightnewsapi.net/v4/articles/"
            self.response = rq.get(self.url)
            self.data = self.response.json()
            return self.data
            
    class Calendar:
        def __init__(self):
            self.state = 0
            
    class Sports:

        def __init__(self):
            self.state = 0
            self.data = self.getData()

        def getData(self):
            self.url = "https://basketball-highlights-api.p.rapidapi.com/matches"
            self.response = rq.get(self.url)
            self.data = self.response.text
            return self.data

    # Betting

    class Files:
        def __init__(self):
            self.state = 0

    class Home:
        def __init__(self):
            self.state = 0

    class Explorer:
    
        def __init__(self):
            self.state = 0
        class Mars:
            def __init__(self):
                self.state = 0

                self.manifestUrl = 'https://api.nasa.gov/mars-photos/api/v1/manifests/perseverance/?api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
                self.manifest = self.getManifestData(self.manifestUrl)
                
                self.sol = self.getSol(self.manifest)

                self.imagesUrl = 'https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?sol='+ str(self.sol) + '&api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
                self.waypointsUrl = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'

                self.images = self.getImages(self.imagesUrl)
                self.coordinates = self.getWaypoints(self.waypointsUrl)

                self.data = {
                    'images': self.images,
                    'coords': self.coordinates
                }

            def getManifestData(self,url): # gets manifest data
                self.data = rq.get(url).json()
                self.data = self.data['photo_manifest'] # pandas
                return self.data

            def getSol(self,manifestData):
                self.sol = manifestData['max_sol']
                return self.sol

            def getImages(self,url):

                self.images = []
                self.data = rq.get(url).json()

                self.photos = self.data['photos'] # returns a list of all img dictionaries

                for photo in range(len(self.photos)):
                    self.imageURL = self.photos[photo]['img_src'] # retrieves all photos
                    if self.photos[photo]['camera']['name'] != 'SKYCAM':
                        self.images.append(self.imageURL)

                return self.images

            def getWaypoints(self,url):

                self.coords = []
                self.coord = {}
                self.data = rq.get(url).json()
                self.data = self.data['features']

                for waypoint in range(len(self.data)):
                    self.coord = {'lon': float(self.data[waypoint]['properties']['lon']), 'lat': float(self.data[waypoint]['properties']['lat']),'sol':int(self.data[waypoint]['properties']['sol'])}
                    self.coords.append(self.coord)
                return self.coords

            def getDistance(self,coordsJson):
                distances = []
                distanceData = coordsJson
                for i in range(len(distanceData)):
                    distances.append([distanceData[i]['properties']['dist_m'],distanceData[i]['properties']['sol']])
                distances = pd.DataFrame(distances) #data frame
                return distances
        

"""
print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_sunrise = daily.Variables(2).ValuesAsNumpy()
daily_sunset = daily.Variables(3).ValuesAsNumpy()
daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
daily_rain_sum = daily.Variables(5).ValuesAsNumpy()
daily_showers_sum = daily.Variables(6).ValuesAsNumpy()
daily_precipitation_hours = daily.Variables(7).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset
daily_data["daylight_duration"] = daily_daylight_duration
daily_data["rain_sum"] = daily_rain_sum
daily_data["showers_sum"] = daily_showers_sum
daily_data["precipitation_hours"] = daily_precipitation_hours

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)
"""
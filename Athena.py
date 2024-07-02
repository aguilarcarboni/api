from datetime import datetime
import time
import pytz

import ast
import os
import requests as rq
import pandas as pd
from pandas.tseries.offsets import BDay

import yfinance as yf

import openmeteo_requests
import requests_cache
from retry_requests import retry

from openai import AsyncOpenAI

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

class Athena:
           
    class Brain:
        def __init__(self):
   
            self.client = AsyncOpenAI(
                organization=os.getenv("OPENAI_ORGANIZATION_ID"),
                project=os.getenv("OPENAI_PROJECT_ID"),
            )

        async def ask(self, message):

            runs = await self.client.beta.threads.runs.list(os.getenv('ATHENA_THREAD_ID'))
            for run in runs.to_dict()['data']:
                if run['status'] in ['in_progress', 'incomplete', 'queued', 'requires_action', 'cancelling']:
                    runs = await self.client.beta.threads.runs.cancel(run['id'], thread_id=os.getenv('ATHENA_THREAD_ID'))
                

            await self.addMessageToThread(message)
            message_content = await self.getAnswer()
            return message_content
            
        async def addMessageToThread(self, user_question):
            # Create a message inside the thread
            message = await self.client.beta.threads.messages.create(
                thread_id=os.getenv('ATHENA_THREAD_ID'),
                role="user",
                content= user_question
            )
            return message
    
        async def getAnswer(self):

            # run assistant
            print("Running Athena...")
            run =  await self.client.beta.threads.runs.create(
                thread_id=os.getenv('ATHENA_THREAD_ID'),
                assistant_id=os.getenv('ATHENA_ASSISTANT_ID')
            )

            # wait for the run to complete
            while True:
                runInfo = await self.client.beta.threads.runs.retrieve(thread_id=os.getenv('ATHENA_THREAD_ID'), run_id=run.id)
                if runInfo.status == 'requires_action':
                    # Define the list to store tool outputs
                    tool_outputs = []
                
                    # Loop through each tool in the required action section
                    print(runInfo.required_action)
                    for tool in runInfo.required_action.submit_tool_outputs.tool_calls:
                        print(tool)

                        if tool.function.name == "save_info_to_db":

                            print('Athena saving info to database.')
                            arguments = ast.literal_eval(tool.function.arguments)

                            print(arguments, tool.function.arguments)

                            # Query database
                            Mongo = Athena.Database()
                            
                            if arguments['query'] != 'NONE':
                                Mongo.updateDocumentInCollection(arguments['data'], arguments['query'], arguments['path'])
                            else:
                                Mongo.insertDocumentToCollection(arguments['data'], arguments['path'])

                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output":"Query successful."
                            })

                        elif tool.function.name == "get_info_from_db":
                            
                            print('Athena fetching from database.')
                            arguments = ast.literal_eval(tool.function.arguments)

                            print(arguments, tool.function.arguments)

                            Mongo = Athena.Database()
                            document = Mongo.queryDocumentInCollection(arguments['query'],arguments['path'])

                            print(document)

                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output":str(document)
                            })
                        
                        elif tool.function.name == "get_file_from_google_drive":

                            print('Athena fetching from Drive.')
                            arguments = ast.literal_eval(tool.function.arguments)

                            print(arguments, tool.function.arguments)

                            Drive = Athena.Drive()
                            fileId = Drive.queryForFile(arguments['path'], arguments['file_name'])

                            print(fileId)

                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output":str({'data':fileId})
                            })
                        
                    
                    # Submit all tool outputs at once after collecting them in a list
                    if tool_outputs:
                        try:
                            run = await self.client.beta.threads.runs.submit_tool_outputs(
                                thread_id=os.getenv('ATHENA_THREAD_ID'),
                                run_id=run.id,
                                tool_outputs=tool_outputs
                            )
                            print("Tool outputs submitted successfully.")
                        except Exception as e:
                            print("Failed to submit tool outputs:", e)
                            break
                    else:
                        print("No tool outputs to submit.")
                        break

                if runInfo.completed_at:
                    elapsed = runInfo.completed_at - runInfo.created_at
                    elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                    print(f"Run completed")
                    break

                print("Waiting 1sec...")
                time.sleep(1)
                print(runInfo.status)

            print("All done...")
            
            # Get messages from the thread
            messages = await self.client.beta.threads.messages.list(
                thread_id=os.getenv('ATHENA_THREAD_ID'),
            )
            message = messages.data[0]
            message_content = message.content[0].text.value
            return message_content

    class DateAndTime:
        def __init__(self):
            self.timezone = pytz.timezone('America/Costa_Rica')
            self.currentDateTime = datetime.now(self.timezone)

            self.currentDateTimeString = self.getCurrentDateTimeString()
            self.currentDate = self.getCurrentDate()
            self.currentTime = self.getCurrentTime()
            self.lastWorkingDate = self.getLastWorkingDate()
            
        def getCurrentDateTimeString(self):
            # Get the current time in CST
            dateTimeString = self.currentDateTime.strftime('%Y%m%d%H%M%S')
            return dateTimeString

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
            self.forecast = self.getHourlyFourDayForecast()
            self.currentWeather = self.getCurrentWeather()

        def connectToOpenMeteo(self,lat,lon):

            # Setup the Open-Meteo API client with cache and retry on error
            cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
            retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
            openmeteo = openmeteo_requests.Client(session = retry_session)

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
            responses = openmeteo.weather_api(self.url, params=self.params)
            return responses[0]

        def getCurrentWeather(self):

            # Current values. The order of variables needs to be the same as requested.
            current = self.service.Current()
            data = {
                'current_temperature_2m':current.Variables(0).Value(),
                'current_relative_humidity_2m':current.Variables(1).Value(),
                'current_is_day':current.Variables(2).Value(),
                'current_rain':current.Variables(3).Value(),
                'current_showers':current.Variables(4).Value(),
                'current_weather_code':current.Variables(5).Value()
            }
            return data
        
        
        def getHourlyFourDayForecast(self):

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = self.service.Hourly()
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

            hourly_data["temperature_2m"] = hourly_temperature_2m
            hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
            hourly_data["precipitation_probability"] = hourly_precipitation_probability
            hourly_data["rain"] = hourly_rain
            hourly_data["showers"] = hourly_showers
            hourly_data["weather_code"] = hourly_weather_code
            hourly_data["visibility"] = hourly_visibility
            hourly_data["uv_index"] = hourly_uv_index
            hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
            hourly_data["is_day"] = hourly_is_day

            hourly_dataframe = pd.DataFrame(data = hourly_data)
            self.data = hourly_dataframe.to_dict(orient="records")
            return self.data

    class Market:
        def __init__(self, tickers):

            self.historicalStocksData = self.getMarketData(tickers)

        def getMarketData(self, tickers):
            
            marketData = {}

            for ticker in tickers:
                
                tickerData = yf.Ticker(ticker)

                end_date = datetime.now().strftime('%Y%m%d')
                end_date_f = datetime.now().strftime('%Y-%m-%d')

                # get all stock info
                tickerData = tickerData.history(start='2024-03-15', end=end_date_f)
                tickerHistory = {}
                prevDate = '20240315'

                for date in (tickerData.index):
                    date = str('%04d' % date.year) + str('%02d' % date.month) + str('%02d' % date.day)
                    tickerHistory[date] = {}
                    for cat in tickerData.iloc[0,:].index:
                        info = tickerData.loc[date,:][cat]
                        tickerHistory[date][cat] = info

                marketData[ticker] = tickerHistory

            for ticker in marketData:
                for date in marketData[ticker]:
                    marketData[ticker][date]['Change $'] = marketData[ticker][date]['Close'] - marketData[ticker][prevDate]['Close']
                    marketData[ticker][date]['Change %'] = (marketData[ticker][date]['Close'] - marketData[ticker][prevDate]['Close'])/marketData[ticker][date]['Close'] * 100
                    prevDate = date

            return marketData

        def getLastPrice(self, ticker):
            lastWorkingDate = Athena.DateAndTime().lastWorkingDate
            lastPrice = self.historicalStocksData[ticker][lastWorkingDate]['Close']
            return lastPrice
        
    class News:
        def __init__(self):
            self.state = 0
        def getSpaceFlightNews(self):
            url = "https://api.spaceflightnewsapi.net/v4/articles/"
            response = rq.get(url)
            data = response.json()
            return data
            
    class Calendar:
        def __init__(self):
            self.state = 0
            
    class Sports:

        def __init__(self):
            self.state = 0

    class Betting:
        def __init__(self):
            state = 0

    class Home:
        def __init__(self):
            self.state = 0

    class Drive:

        def __init__(self):
            SCOPES = ['https://www.googleapis.com/auth/drive']
            creds = Credentials.from_authorized_user_file("creds/GoogleAuthedToken.json", SCOPES)
            self.service = build("drive", "v3", credentials=creds)

        # Query a file inside Drive
        def queryForFile(self, path, file_name):

            print(path, file_name)

            path = path + '/' + file_name
            paths = path.split('/')
            
            current_path = ''

            parentId = 'root'
            files = []

            for index, path in enumerate(paths):
                try:
                    page_token = None

                    try:
                        while True:

                            print(files)

                            response = (
                                self.service.files()
                                .list(
                                    q=f"name='{path}' and trashed = false and '{parentId}' in parents",
                                    spaces="drive",
                                    fields="nextPageToken, files(id, name)",
                                    pageToken=page_token,
                                )
                                .execute()
                            )
                                
                            files.append(response.get("files"))
                            parentId = response.get("files")[0]['id']

                            page_token = response.get("nextPageToken", None)
                            if page_token is None:
                                break

                    except HttpError as error:
                        print(f"An error occurred: {error}")
                        files = None

                    current_path += '/' + path
                    print('\nFound:\n', files[0], current_path)

                except:
                    print('Not found.')
                    break
            
            return files[len(files) - 1]

    class Database:
        def __init__(self):

            # Create a new client and connect to the server
            uri = "mongodb+srv://aguilarcarboni:NewYork2020@athena.jcntnxw.mongodb.net/?retryWrites=true&w=majority&appName=Athena"
            self.client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
            print('Initialized client')

        def insertDocumentToCollection(self, data, path):

            data = ast.literal_eval(data)
            collection = self.client['main']

            paths = path.split('/')
            current_path = ''

            collection = collection[path]

            data = [data]
            collection.insert_many(data)

            print('Inserted document.')
            
            return
    
        def updateDocumentInCollection(self, data, query, path):

            query = ast.literal_eval(query)
            data = ast.literal_eval(data)

            collection = self.client['main']

            paths = path.split('/')
            current_path = ''

            collection = collection[path]
            document = collection.update_many(query, {
                '$set': data
            })
            print(document)
            
            return document


        def queryDocumentInCollection(self, query, path):
            print(path, query)

            query = ast.literal_eval(query)
            collection = self.client['main']

            paths = path.split('/')
            current_path = ''

            collection = collection[path]
            document = collection.find_one(query)
            print(document)
            
            return document
                
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
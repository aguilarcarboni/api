import logging
from datetime import datetime
import pytz

import io
import csv

import requests as rq
import pandas as pd
from pandas.tseries.offsets import BDay

import yfinance as yf

from bs4 import BeautifulSoup

import openmeteo_requests
import requests_cache
from retry_requests import retry

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload

from google_auth_oauthlib.flow import InstalledAppFlow

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import certifi

import os

from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

from websocket import create_connection
import json

# Configure logging with Rich
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "critical": "bold white on red",
})
console = Console(theme=custom_theme)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

def __init__(flask_app):
    logger.info('Initializing laserfocus...')
    global url, app
    url = 'https://laserfocus-api.onrender.com'
    app = flask_app

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
        logger.info(f"Initializing Weather for lat: {lat}, lon: {lon}")
        self.service = self.connectToOpenMeteo(lat,lon)
        self.forecast = self.getHourlyFourDayForecast()
        self.currentWeather = self.getCurrentWeather()

    def connectToOpenMeteo(self,lat,lon):
        logger.info("Connecting to OpenMeteo API")
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
        logger.info("Getting current weather")
        # Current values. The order of variables needs to be the same as requested.
        current = self.service.Current()
        data = {
            'temperature':current.Variables(0).Value(),
            'humidity':current.Variables(1).Value(),
            'is_day':current.Variables(2).Value(),
            'rain':current.Variables(3).Value(),
            'showers':current.Variables(4).Value(),
            'weather_code':current.Variables(5).Value()
        }
        return data
    
    
    def getHourlyFourDayForecast(self):
        logger.info("Getting hourly four-day forecast")
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
        self.data = hourly_dataframe.to_dict(orient="records")
        return self.data

class Market:
    def __init__(self):
        self.tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'V']

    def getMarketData(self):
        marketData = {}

        for ticker in self.tickers:
            
            tickerData = yf.Ticker(ticker)

            end_date = datetime.now().strftime('%Y-%m-%d')

            # get all stock info
            tickerData = tickerData.history(start='2024-03-15', end=end_date)
            tickerHistory = {}
            prevDate = '20240315'

            for date in (tickerData.index):
                date = str('%04d' % date.year) + str('%02d' % date.month) + str('%02d' % date.day)
                tickerHistory[date] = {}
                for category in tickerData.iloc[0,:].index:
                    info = tickerData.loc[date,:][category]
                    tickerHistory[date][category] = info
                
                tickerHistory[date]['Change $'] = tickerHistory[date]['Close'] - tickerHistory[prevDate]['Close']
                tickerHistory[date]['Change %'] = tickerHistory[date]['Change $'] / tickerHistory[prevDate]['Close']
                prevDate = date

            marketData[ticker] = tickerHistory

        logger.info(f"[green]Retrieved market data for {len(marketData)} tickers[/green]", extra={'markup':True})
        return marketData
    
class News:

    def __init__(self):
        self.state = 0
    
    def scrapeCNNHeadlines(self):

        url = 'https://www.cnn.com'
        soup = Browser().scraper(url)

        # Find the sections containing headlines
        headlines = soup.find_all('div', class_='stack__items')

        news  = []
        for headline in headlines:
            for link in headline.find_all('a'):
                if ('•' not in link.get_text().strip()):
                    news.append({'title':link.get_text().strip(), 'url':url + link.get('href')})

        return {'status':'success', 'content':news}
            
class Sports:

    def __init__(self):
        self.state = 0

class Betting:
    def __init__(self):
        state = 0

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

class Browser:
    def __init__(self):

        self.state = 0

    def scraper(self, url):
        logger.info(f"Scraping URL: {url}")
        # Send a request to fetch the HTML content
        response = rq.get(url)
        if response.status_code != 200:
            logger.info("[red]Failed to retrieve the web page.[/red]", extra={'markup':True})
            return

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        logger.info(f"[green]Successfully scraped URL.[/green]", extra={'markup':True})
        return soup


# TODO WORK ON THIS
# TODO MAKE THIS MANY FILES
# TODO ADD DATABASE STUFF
# TODO FINISH WALLET STUFF
# TODO ADD SOME HOME STUFF

class Home:

    def __init__(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0NDhhOWQ2MDFkYzk0YzgxYWI3YThhNDQ1NzY3OGYwOCIsImlhdCI6MTcyNTczNjk4OSwiZXhwIjoyMDQxMDk2OTg5fQ.bepKyJyKb4mS5lbDzfXFRC25pk53oiChreza4rvL3q8"
        self.ws = create_connection("ws://oasis.local:8123/api/websocket")
        self.nextId = 0
        print(self.ws.recv())
        self.ws.send(json.dumps({'type': 'auth', 'access_token': token}))
        print(self.ws.recv())
    
    def getNextId(self):
        self.nextId += 1
        return self.nextId

    def light_on(self, lightId):
        payload = {
        "id": self.getNextId(),
        "type": "call_service",
        "domain": "light",
        "service": "turn_on",
        "target": {
            "entity_id": lightId
            },
        }
        self.ws.send(json.dumps(payload))
        return {'status':'success', 'content':self.ws.recv()}

    def light_off(self, lightId):
        payload = {
        "id": self.getNextId(),
        "type": "call_service",
        "domain": "light",
        "service": "turn_off",
        "target": {
            "entity_id": lightId
            },
        }
        self.ws.send(json.dumps(payload))
        return {'status':'success', 'content':self.ws.recv()}
    
    def get_states(self):
        payload = {
        "id": self.getNextId(),
        "type": "get_states",
        }
        self.ws.send(json.dumps(payload))
        return {'status':'success', 'content':self.ws.recv()}

class Drive:

    def __init__(self):

        logger.info("Initializing Google Drive client")

        SCOPES = ['https://www.googleapis.com/auth/drive']

        # TODO replace with env
        flow = InstalledAppFlow.from_client_secrets_file(
          "creds/credentials.json", SCOPES
      )
        creds = flow.run_local_server(port=0)
        
        self.service = build("drive", "v3", credentials=creds)

        logger.info("[green]Successfully initialized Google Drive client[/green]", extra={'markup':True})

    # Add upload files
    # Add create folder?

    # Modify files?

    # Delete files

    # Remove this?
    def queryForFile(self, path, file_name):

        logger.info(f"Querying for file: {path}/{file_name}")

        path = path + '/' + file_name
        paths = path.split('/')

        parentId = 'root'
        files = []

        for index, path in enumerate(paths):
            try:

                    response = (
                        self.service.files()
                        .list(
                            q=f"name='{path}' and trashed = false and '{parentId}' in parents",
                            spaces="drive",
                            fields="files(id, name)",
                        )
                        .execute()
                    )
                    
                    filesResponse = response.get("files")
                    logger.info(filesResponse)
                    files.append(filesResponse[0])

                    parentId = files[index]['id']

            except HttpError as error:
                logger.info(f"[red]An error occurred. {error}[/red]", extra={'markup':True})
                return {'status':'error'}
            
            except:
                logger.info("[red]Error querying file.[/red]", extra={'markup':True})
                return {'status':'no_data', 'content':None}
        
        logger.info(f"[green]Successfully queried file: {files[len(files) - 1]}[/green]", extra={'markup':True})
        return {'content':files[len(files) - 1], 'status':'success'}

    def queryForFiles(self, path):

        logger.info(f"Querying for files in: {path}")

        path = path + '/'
        paths = path.split('/')

        parentID = 'root'

        for index, currentPath in enumerate(paths):

            query = f"trashed = false and '{parentID}' in parents"

            if index < len(paths) - 1:
                query =f"name='{currentPath}' and trashed = false and '{parentID}' in parents"

            if path == '/':
                query =f"trashed = false and 'root' in parents"

            try:

                    response = (
                        self.service.files()
                        .list(
                            q=query,
                            spaces="drive",
                            fields="files(id, name)",
                        )
                        .execute()
                    )

                    parentID = response['files'][0]['id']

            except HttpError as error:
                logger.info(f"[red]An error occurred. {error}[/red]", extra={'markup':True})
                return {'status':'error'}
        
            except:
                logger.info("[red]Error querying files.[/red]", extra={'markup':True})
                return {'status':'no_data', 'content':None}
        
        logger.info(f"[green]Successfully queried files in: {paths[len(paths) - 1]}[/green]", extra={'markup':True})
        return {'content':response, 'status':'success'}

    def downloadFile(self, fileId):

        logger.info(f"Downloading file with ID: {fileId}")

        try:
            request = self.service.files().get_media(fileId=fileId)
            downloaded_file = io.BytesIO()
            downloader = MediaIoBaseDownload(downloaded_file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"[green]Download {int(status.progress() * 100)}.[/green]", extra={'markup':True})

        except HttpError as error:
            logger.info(f"[red]An error occurred: {error}[/red]", extra={'markup':True})
            downloaded_file = None
            return ({'status':'error'})
        
        except:
            logger.info("[red]Error downloading file.[/red]", extra={'markup':True})
            return {'status':'no_data', 'content':None}
        
        logger.info(f"[green]Successfully downloaded file.[/green]", extra={'markup':True})
        return {'content':downloaded_file.getvalue(), 'status':'success'}

class Database:

    def __init__(self):
        
        logger.info("Initializing database client.")
        # Create a new client and connect to the server
        uri = os.getenv("MONGODB_URI")

        self.client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
        logger.info("[green]Successfully initialized database client.[/green]", extra={'markup':True})

    def convertIds(self, data, canConvert):

        if isinstance(data, dict):
                    
            for key, value in data.items():
                
                if 'id' in key or 'Id' in key:
                    canConvert = True

                data[key] = self.convertIds(value, canConvert)
                    
        if isinstance(data, str):
            if (canConvert):
                logger.info(f'Converting ({data}) to ObjectId.')
                try:
                    return ObjectId(data)
                except:
                    logger.info(f'({data}) is not an ObjectId. Returning original data.')
                    return data
            
        elif isinstance(data, list):
            for index, item in enumerate(data):
                data[index] = self.convertIds(item, canConvert)

        return data

    # Replace individual CRUD operations?

    def queryDocumentInCollection(self, database, table, query):

        logger.info('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})
        
        query = self.convertIds(query, False)
    
        if database not in self.client.list_database_names():
            logger.info('No database with that name found.')
            return {'status':'error', 'content':'No database with that name found.'}
        
        db = self.client[database]
        
        if table not in db.list_collection_names():
            logger.info('No table with that name found.')
            return {'status':'error', 'content':'No table with that name found.'}
        
        tb = db[table]
        
        entry = tb.find_one(query)
        
        if entry is not None:
            logger.info('[green]Successfully queried entry.[/green]', {'content':entry}, extra={'markup':True})
            return {'status':'success', 'content':entry}
        else:
            logger.info('[red]Entry not found.[/red]', extra={'markup':True})
            return {'status':'no_data', 'content':None}
    
    def queryDocumentsInCollection(self, database, table, query):

        logger.info('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})
        
        query = self.convertIds(query, False)
    
        if database not in self.client.list_database_names():
            logger.info('[red]No database with that name found.[/red]', extra={'markup':True})
            return {'status':'error', 'content':'No database with that name found.'}
        
        db = self.client[database]
        
        if table not in db.list_collection_names():
            logger.info('[red]No table with that name found.[/red]', extra={'markup':True})
            return {'status':'error', 'content':'No table with that name found.'}
        
        tb = db[table]
        
        entry = tb.find(query)
        
        if entry is not None:
            logger.info('[green]Successfully queried entry.[/green]', {'content':entry}, extra={'markup':True})
            return {'status':'success', 'content':entry}
        else:
            logger.info('[red]Entry not found.[/red]', extra={'markup':True})
            return {'status':'no_data', 'content':None}

    def insertDocumentToCollection(self, database, table, data, context):

        logger.info('Inserting entry to table in Database.')
        logger.info('Data:', {'database':database, 'table':table, 'data':data})
        
        for key in data:
            if 'id' in key or 'Id' in key:
                logger.info(f'Converting id {key} to ObjectId.')
                data[key] = ObjectId(data[key])

        for key in context:
            if 'id' in key or 'Id' in key:
                logger.info(f'Converting id {key} to ObjectId.')
                context[key] = ObjectId(context[key])

        if database not in self.client.list_database_names():
            logger.info('No database with that name found.')
            return {'status':'error', 'content':'No database with that name found.'}

        db = self.client[database]

        if table not in db.list_collection_names():
            logger.info('No table with that name found.')
            return {'status':'error', 'content':'No table with that name found.'}
    
        tb = db[table]

        try:
            insertedData = tb.insert_one(data)
        except:
            logger.info('Error inserting entry.')
            return {'status':'error'}

        logger.info('Successfully inserted entry.\n')
        insertedId = insertedData.inserted_id

        logger.info('Adding dependencies that relate to entry.')

        dependencies = self.insertDependencies(table, data, ObjectId(insertedId), context)
    
        return {'status':'success', 'content':{'data':str(insertedId), 'dependencies':dependencies}}

    def deleteDocumentInCollection(self, database, table, query):

        logger.info('Deleting entry in table in Database.', {'database':database, 'table':table, 'query':query})

        for key in query:
            if 'id' in key or 'Id' in key:
                logger.info(f'Converting id {key} to ObjectId.')
                query[key] = ObjectId(query[key])

        if database not in self.client.list_database_names():
            logger.info('No database with that name found.')
            return {'status':'error', 'content':'No database with that name found.'}
        
        db = self.client[database]

        if table not in db.list_collection_names():
            logger.info('No table with that name found.')
            return {'status':'error', 'content':'No table with that name found.'}
        
        tb = db[table]

        try:
            deletedData = tb.find_one_and_delete(query)
        except:
            logger.info('Error deleting entry.')
            return {'status':'error'}

        logger.info('Successfully deleted entry.')
        logger.info(deletedData)
        deletedId = deletedData['_id']
        logger.info(deletedId, type(deletedId))

        logger.info('Deleting dependencies that relate to entry.')
        dependencies = self.deleteDependencies(table, ObjectId(deletedId), deletedData)

        return {'status':'success', 'content':{'data':str(deletedData), 'dependencies':dependencies}}

    def insertDependencies(self, table, data, insertedId, context):

        dependencies = {}
        match table:
            case 'user':
                
                result = self.insertDocumentToCollection('spaces', 'space', {'name':str(data['name']) + 's Space"}'}, {'userId':str(insertedId)})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'event':
                
                # Insert space event relationship
                result = self.insertDocumentToCollection('spaces', 'space-event', {'eventId':str(insertedId), 'spaceId':str(context['spaceId'])}, {})
                dependencies['space-event'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'space':

                # Insert user space relationship
                if ('userId' in list(context.keys())):
                    result = self.insertDocumentToCollection('users', 'user-space', {'userId':str(context['userId']), 'spaceId':str(insertedId)}, {})
                    dependencies['user-space'] = result['content']['data']

                # Insert project space relationship
                elif ('projectId' in list(context.keys())):
                    result = self.insertDocumentToCollection('projects', 'project-space', {'projectId':str(context['projectId']), 'spaceId':str(insertedId)}, {})
                    dependencies['project-space'] = result['content']['data']

                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'project':

                # Insert user project relationship
                result = self.insertDocumentToCollection('users', 'user-project', {'userId':str(context['userId']), 'projectId':str(insertedId)}, {})
                dependencies['user-project'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

                # Create project's space
                result = self.insertDocumentToCollection('spaces', 'space', {'name':'Test Space'}, {'projectId':str(insertedId)})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case _:
                pass

        logger.info('Dependencies:', dependencies)
        return dependencies

    def deleteDependencies(self, table, deletedId, context):

        dependencies = {}
        match table:

            case 'user':

                # Remove users's space
                result = self.deleteDocumentInCollection('projects', 'user-space', {'userId':str(deletedId)})

                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'user-space':

                result = self.deleteDocumentInCollection('spaces', 'space', {'spaceId':str(context['spaceId'])})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]
                                
            case 'user-project':
                pass


            case 'space':
                pass


            case 'event':

                result = self.deleteDocumentInCollection('spaces', 'space-event', {'eventId':str(deletedId)})
                dependencies['space-event'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]


            case 'project-space':

                result = self.deleteDocumentInCollection('spaces', 'space', {'_id':str(context['spaceId'])})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'project':

                # Remove project's space
                result = self.deleteDocumentInCollection('projects', 'project-space', {'projectId':str(deletedId)})
                dependencies['project-space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

                # Remove user's project
                result = self.deleteDocumentInCollection('users', 'user-project', {'projectId':str(deletedId)})
                dependencies['user-project'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case _:
                pass

        return dependencies

class Wallet:

    class BAC:

        def __init__(self):
            self.accounts = [
                {
                    'name':'Cash',
                    'account_id':'CR83010200009295665295'
                }
            ]

        def generateStatements(self, account, file_name):
            logger.info(f"Generating statements for account: {account}, file: {file_name}")
            # Change path to account
            path = 'Personal/Wallet/Statements/BAC/' +  account + '/Sources'
            dictToSend = {'path':path, 'file_name':file_name}
            res = rq.post('https://laserfocus-api.onrender.com' + '/drive/query_file', json=dictToSend)

            # Get month that the statement is for
            period = file_name.split('.')[0]

            # Download file in plain text
            binaryFile = res.content
            file_text = binaryFile.decode('latin1')

            # Parse statements
            df_statements, account_number = self.parseStatements(file_text)

            # Validate account
            accounts = [{'id':'CR83010200009295665295', 'name':'Cash'}]
            account_number = account_number.strip()
            for acct in accounts:
                if acct['id'] == account_number and acct['name'] == account:
                    acct = acct['name']

            # Get debits and credits
            df_debits, df_credits = self.getEntries(df_statements)

            # Categorize entries
            df_debits = self.categorizeStatements(df_debits)
            df_credits = self.categorizeStatements(df_credits)

            # Post process data
            df_all = pd.concat([df_debits, df_credits])
            df_all['Total'] = df_all['Credit'].astype(float) - df_all['Debit'].astype(float)
            df_all = df_all.sort_values(by='Date')

            # Save to drive TODO CREATE FUNCTION
            # Output path: Personal/Wallet/Statements/{Bank}/{AccountNumber}
            # Output file name: MMYYYY.csv

            try:
                df_all.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/{account}/Processed/{period}.csv', index=False)
                logger.info(f"Successfully saved processed data to {period}.csv")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}")
                return {'error':'error'}
            
            logger.info('Processed data.')
            
            return {'status':'success'}

        def parseStatements(self, file_text):
            logger.info("Parsing statements")
            rows = file_text.splitlines()
            parsed_csv = csv.reader(rows)
            account_number = None

            rows = []

            write = False
            previous_row = None
            
            for row in parsed_csv:
                if len(row) >  0:
                    logger.debug(f"Parsing row: {row}")

                    if previous_row is not None and len(previous_row) > 0 and previous_row[0] == 'Fecha de Transacción':
                        write = True

                    if row[0] == '':
                        write = False
                    
                    if (write):
                        rows.append(row)

                    if row[0].isdigit():
                        account_number = row[2]
                    logger.debug(f"Account number: {account_number}")

                previous_row = row
                
            data = []
            for row in rows:
                try:
                    date = datetime.strptime(row[0], '%d/%m/%Y')
                except:
                    date = datetime.strptime(row[0], '%d/%m/%y')
                    
                transaction = {'Date':date, 'Reference':row[1], 'Code':row[2], 'Description':row[3], 'Debit':row[4], 'Credit':row[5], 'Balance':row[6], 'Category':'', 'Q': 'Q1' if date.day < 15 else 'Q2'}
                data.append(transaction)

            df_statements = pd.DataFrame(data)
            df_statements['Date'] = pd.to_datetime(df_statements['Date'], format='%d/%m/%Y')

            return df_statements, account_number

        def getEntries(self, df_statements):
            logger.info("Getting entries from statements")
            df_debits = df_statements[df_statements['Credit'].astype(float) == 0].copy()

            df_credits = df_statements[df_statements['Debit'].astype(float) == 0].copy()

            return df_debits, df_credits
        
        def categorizeStatements(self, df_statements):
            logger.info("Categorizing statements")
            # Debits
            if len(df_statements[df_statements['Debit'].astype(float) == 0]) == 0:
            
                for index, row in df_statements.iterrows():

                    for subscription in ['COMPA', 'SEGURO BELD', 'COMPASS']:
                        if subscription in row['Description']:
                            df_statements.loc[index, 'Category'] = 'Subscriptions'

                    # Categorize income
                    for gas_station in ['DELTA', 'SERVICIO', 'SERVICENTRO', 'GAS', 'Uber Rides']:
                        if gas_station in row['Description']:
                            df_statements.loc[index,'Category'] = 'Transportation'

                    for savings_account in ['960587293', 'SAVINGS']:
                        if savings_account in row['Description']:
                            df_statements.loc[index,'Category'] = 'Savings'


            # Credits             
            else:

                for index, row in df_statements.iterrows():

                    for savings_account in ['960587293', 'SAVINGS']:
                        if savings_account in row['Description']:
                            df_statements.loc[index,'Category'] = 'Savings'

                    for income_source in ['DEP', '1Q', '2Q', 'INCOME']:
                        if income_source in row['Description']:
                            df_statements.loc[index,'Category'] = 'Income'
                
                    
            return df_statements

        def manuallyCategorizeStatements(self, df_statements):
            logger.info("Manually categorizing statements")
            for index, row in df_statements[df_statements['Category'] == ''].iterrows():
                logger.info(f"\n{row}")
                category = input('Enter category for statement:')
                df_statements.loc[index, 'Category'] = category

            return df_statements

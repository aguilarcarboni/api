import logging
from datetime import datetime
import pytz

import io
import csv

import requests as rq
import pandas as pd
from pandas.tseries.offsets import BDay

from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

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

from typing import Any, Dict, Union

class Response:
    def __init__(self, status: str, content: Any):
        self.status = status
        self.content = content

    @classmethod
    def success(cls, content: Any) -> Dict[str, Union[str, Any]]:
        return cls("success", content).to_dict()

    @classmethod
    def error(cls, content: Any) -> Dict[str, Union[str, Any]]:
        return cls("error", content).to_dict()

    def to_dict(self) -> Dict[str, Union[str, Any]]:
        return {
            "status": self.status,
            "content": self.content
        }

class ColorLogger:
    def __init__(self):
        custom_theme = Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "bold red",
            "critical": "bold white on red",
        })
        self.console = Console(theme=custom_theme)
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("rich")

    def info(self, message):
        self.logger.info(f"[blue]{message}[/blue]", extra={'markup': True})

    def success(self, message):
        self.logger.info(f"[green]{message}[/green]\n", extra={'markup': True})

    def error(self, message):
        self.logger.error(f"[red]{message}[/red]", extra={'markup': True})

# Create a global instance of ColorLogger
color_logger = ColorLogger()

class Location:
    def __init__(self):
        color_logger.info("Initializing Location.")
        self.coordinates = {'lat': 9.9281, 'lon': -84.2376}
        self.timezone = pytz.timezone('America/Costa_Rica')
        color_logger.success("Successfully initialized Location.")

Location = Location()

class DateAndTime:
    def __init__(self):
        color_logger.info("Initializing Date and Time.")
        self.timezone = Location.timezone
        self.currentDateTime = datetime.now(self.timezone)
        color_logger.success("Successfully initialized Date and Time.")

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


""""""
# TODO
""""""

# Get rid of this api
class Weather:
    def __init__(self,lat,lon):
        color_logger.info(f"Initializing Weather for lat: {Location.coordinates['lat']}, lon: {Location.coordinates['lon']}.")
        self.service = self.connectToOpenMeteo(lat,lon)
        self.forecast = self.getHourlyFourDayForecast()
        self.currentWeather = self.getCurrentWeather()
        color_logger.success("Successfully initialized Weather.")

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
            'temperature':current.Variables(0).Value(),
            'humidity':current.Variables(1).Value(),
            'is_day':current.Variables(2).Value(),
            'rain':current.Variables(3).Value(),
            'showers':current.Variables(4).Value(),
            'weather_code':current.Variables(5).Value()
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


# Get news I'm interested in?
class News:

    def __init__(self):
        color_logger.info("Initializing News.")
        self.state = 0
        color_logger.success("Successfully initialized News.")
    
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

        return Response.success(news)

class Sports:

    def __init__(self):
        color_logger.info("Initializing Sports client")
        self.state = 0
        color_logger.success("Successfully initialized Sports client")


# TODO ADD SOME HOME STUFF

class Home:

    def __init__(self):
        color_logger.info("Initializing Oasis.")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0NDhhOWQ2MDFkYzk0YzgxYWI3YThhNDQ1NzY3OGYwOCIsImlhdCI6MTcyNTczNjk4OSwiZXhwIjoyMDQxMDk2OTg5fQ.bepKyJyKb4mS5lbDzfXFRC25pk53oiChreza4rvL3q8"
        try:
            self.ws = create_connection("ws://oasis.local:8123/api/websocket")
        except:
            color_logger.error("Failed to initialize Oasis.")
            return None
        self.nextId = 0
        print(self.ws.recv())
        self.ws.send(json.dumps({'type': 'auth', 'access_token': token}))
        print(self.ws.recv())
        color_logger.success("Successfully initialized Oasis.")
    
    def getNextId(self):
        self.nextId += 1
        return self.nextId

    def get_states(self):
        payload = {
            "id": self.getNextId(),
            "type": "get_states",
        }
        self.ws.send(json.dumps(payload))
        return Response.success(self.ws.recv())
    
    def get_services(self):
        payload = {
            "id": self.getNextId(),
            "type": "get_services",
        }
        self.ws.send(json.dumps(payload))
        return Response.success(self.ws.recv())
    
    def call_service(self, service):
        payload = {
            "id": self.getNextId(),
            "type": "call_service",
            "domain": "homeassistant",
            "service": service,
        }
        self.ws.send(json.dumps(payload))
        return Response.success(self.ws.recv())

    def get_panels(self):
        payload = {
            "id": self.getNextId(),
            "type": "get_panels",
        }
        self.ws.send(json.dumps(payload))
        return Response.success(self.ws.recv())
    
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
        return Response.success(self.ws.recv())

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
        return Response.success(self.ws.recv())
    

# TODO ADD DATABASE STUFF
class Database:

    def __init__(self):
        
        color_logger.info("Initializing Database.")
        # Create a new client and connect to the server
        uri = os.getenv("MONGODB_URI")

        self.client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
        color_logger.success("Successfully initialized Database.")

    def convertIds(self, data, canConvert):

        if isinstance(data, dict):
                    
            for key, value in data.items():
                
                if 'id' in key or 'Id' in key:
                    canConvert = True

                data[key] = self.convertIds(value, canConvert)
                    
        if isinstance(data, str):
            if (canConvert):
                color_logger.info(f'Converting ({data}) to ObjectId.')
                try:
                    return ObjectId(data)
                except:
                    color_logger.info(f'({data}) is not an ObjectId. Returning original data.')
                    return data
            
        elif isinstance(data, list):
            for index, item in enumerate(data):
                data[index] = self.convertIds(item, canConvert)

        return data

    def queryDocumentInCollection(self, database, table, query):

        color_logger.info('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})
        
        query = self.convertIds(query, False)
    
        if database not in self.client.list_database_names():
            color_logger.error('No database with that name found.')
            return Response.error('No database with that name found.')
        
        db = self.client[database]
        
        if table not in db.list_collection_names():
            color_logger.error('No table with that name found.')
            return Response.error('No table with that name found.')
        
        tb = db[table]
        
        entry = tb.find_one(query)
        
        if entry is not None:
            color_logger.success('Successfully queried entry.', {'content':entry})
            return Response.success(entry)
        else:
            color_logger.error('Entry not found.')
            return Response.error('Entry not found')
    
    def queryDocumentsInCollection(self, database, table, query):

        color_logger.info('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})
        
        query = self.convertIds(query, False)
    
        if database not in self.client.list_database_names():
            color_logger.error('No database with that name found.')
            return Response.error('No database with that name found.')
        
        db = self.client[database]
        
        if table not in db.list_collection_names():
            color_logger.error('No table with that name found.')
            return Response.error('No table with that name found.')
        
        tb = db[table]
        
        entry = tb.find(query)
        
        if entry is not None:
            color_logger.success('Successfully queried entry.', {'content':entry})
            return Response.success(entry)
        else:
            color_logger.error('Entry not found.')
            return Response.error('Entry not found')

    def insertDocumentToCollection(self, database, table, data, context):

        color_logger.info(f'Inserting {data} to {table} in {database}.')
        color_logger.info(f'Context: {context}')

        data = self.convertIds(data, False)
        context = self.convertIds(context, False)

        if database not in self.client.list_database_names():
            color_logger.error('No database with that name found.')
            return Response.error('No database with that name found.')

        db = self.client[database]

        if table not in db.list_collection_names():
            color_logger.error('No table with that name found.')
            return Response.error('No table with that name found.')
    
        tb = db[table]

        # Check if item can be inserted

        try:
            insertedData = tb.insert_one(data)
        except:
            color_logger.error('Error inserting entry.')
            return Response.error('Error inserting entry.')

        color_logger.info(f'Successfully inserted {data} to table: {table} in database: {database}.')
        insertedId = insertedData.inserted_id

        color_logger.info(f'Adding dependencies that relate to table: {table}.')

        dependencies = self.insertDependencies(table, data, ObjectId(insertedId), context)
    
        return Response.success({'data':str(insertedId), 'dependencies':dependencies})

    # TODO Dont do this recursively?
    def insertDependencies(self, table, data, insertedId, context):

        dependencies = {}
        match table:

            case 'user':
                
                # Insert user's space and add it to dependencies
                result = self.insertDocumentToCollection('spaces', 'space', {'name':str(data['name']) + 's Space"}'}, {'userId':str(insertedId)})
                dependencies['space'] = result['content']['data']

                # Add space's dependencies to dependencies
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'event':
                
                # Insert space event relationship 
                result = self.insertDocumentToCollection('spaces', 'space-event', {'eventId':str(insertedId), 'spaceId':str(context['spaceId'])}, {})
                dependencies['space-event'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'task':

                # Insert space task relationship
                result = self.insertDocumentToCollection('spaces', 'space-task', {'taskId':str(insertedId), 'spaceId':str(context['spaceId'])}, {})
                dependencies['space-task'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

                # Insert tasks's dependencies

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

        color_logger.info('No more dependencies, going up a level.')
        return dependencies

    def deleteDocumentInCollection(self, database, table, query):

        color_logger.info(f'Deleting entry in {table} in {database}.')
        color_logger.info(f'Query: {query}')

        query = self.convertIds(query, False)

        if database not in self.client.list_database_names():
            color_logger.error('No database with that name found.')
            return Response.error('No database with that name found.')
        
        db = self.client[database]

        if table not in db.list_collection_names():
            color_logger.error('No table with that name found.')
            return Response.error('No table with that name found.')
        
        tb = db[table]

        # Check if item can be deleted

        try:
            deletedData = tb.find_one_and_delete(query)
        except:
            color_logger.error('Error executing deletion.')
            return Response.error('Error executing deletion.')

        # If nothing was deleted
        if (deletedData is None):
            color_logger.error('Entry not found. This may indicate a broken dependency. Check database for orphaned data.')
            color_logger.info(f'Error location: database: {database}, table: {table}, query: {query}')
            return Response.error({'data':None, 'dependencies':{}})
        
        color_logger.info(f'Successfully deleted {deletedData} from table: {table} in database: {database}.')
        color_logger.info(f'Deleting dependencies that relate to table: {table}.')

        dependencies = self.deleteDependencies(table, deletedData)

        status = 'success'
        for key in list(dependencies.keys()):
            if dependencies[key] is None:
                status = 'requires_attention'

        return Response.success({'data':str(deletedData['_id']), 'dependencies':dependencies})

    # TODO Dont do this recursively?
    def deleteDependencies(self, table, deletedData):

        dependencies = {}
        match table:

            case 'user':

                # Remove users's space
                result = self.deleteDocumentInCollection('users', 'user-space', {'userId':str(deletedData['_id'])})
                dependencies['user-space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'user-space':

                # Check deleted data for userId
            
                result = self.deleteDocumentInCollection('spaces', 'space', {'_id':str(deletedData['spaceId'])})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]
                                
            case 'user-project':
                pass


            case 'space':
                # Delete user space relationship IF NOT YET DELETED
                # Delete everything in space
                pass


            case 'event':

                result = self.deleteDocumentInCollection('spaces', 'space-event', {'eventId':str(deletedData['_id'])})
                dependencies['space-event'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'task':

                result = self.deleteDocumentInCollection('spaces', 'space-task', {'taskId':str(deletedData['_id'])})
                dependencies['space-task'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]


            case 'project-space':

                result = self.deleteDocumentInCollection('spaces', 'space', {'_id':str(deletedData['spaceId'])})
                dependencies['space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case 'project':

                # Remove project's space
                result = self.deleteDocumentInCollection('projects', 'project-space', {'projectId':str(deletedData['_id'])})
                dependencies['project-space'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

                # Remove user's project
                result = self.deleteDocumentInCollection('users', 'user-project', {'projectId':str(deletedData['_id'])})
                dependencies['user-project'] = result['content']['data']
                for key in result['content']['dependencies']:
                    dependencies[key] = result['content']['dependencies'][key]

            case _:
                pass

        color_logger.info('No more dependencies, going up a level.')
        return dependencies
    


"""""" 
""""""

# Happy with this
class Drive:

    def __init__(self):

        color_logger.info("Initializing Drive.")

        SCOPES = ['https://www.googleapis.com/auth/drive']

        # TODO replace with env
        creds = Credentials.from_authorized_user_file("creds/token.json", SCOPES)
        self.service = build("drive", "v3", credentials=creds)

        color_logger.success("Successfully initialized Drive.")

    def createFolder(self, folderName, parentFolderId):

        color_logger.info(f"Creating folder: {folderName} in folder: {parentFolderId}")

        fileMetadata = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parentFolderId is not None:
            fileMetadata['parents'] = [parentFolderId]
        else:
            color_logger.error("No parent folder ID provided.")
            return Response.error('No parent folder ID provided.')
        
        folder = self.service.files().create(body=fileMetadata, fields='id, name, parents, mimeType, size, modifiedTime, createdTime').execute()
        color_logger.success(f"Successfully created folder: {folderName} in folder: {parentFolderId}")
        return Response.success(folder)

    # Upload folder

    # Upload files

    def uploadFileWithPath(self, filePath, parentFolderId):
        color_logger.info(f"Uploading file: {filePath} to folder: {parentFolderId}")
        fileMetadata = {'name': os.path.basename(filePath)}

        if parentFolderId is not None:
            fileMetadata['parents'] = [parentFolderId]
        else:
            color_logger.error("No parent folder ID provided.")
            return Response.error('No parent folder ID provided.')
        
        media = MediaFileUpload(filePath, resumable=True)
        f = self.service.files().create(body=fileMetadata, media_body=media, fields='id, name, parents, mimeType, size, modifiedTime').execute()
        print(f)
        color_logger.success(f"Successfully uploaded file: {filePath} to folder: {parentFolderId}")
        return Response.success(f)

    def uploadFile(self, fileName, rawFile, parentFolderId):
        color_logger.info(f"Uploading file: {fileName} to folder: {parentFolderId}")
        fileMetadata = {'name': fileName}

        if parentFolderId is not None:
            fileMetadata['parents'] = [parentFolderId]
        else:
            color_logger.error("No parent folder ID provided.")
            return Response.error('No parent folder ID provided.')
        print(f)
        try:
            media = MediaIoBaseUpload(rawFile, resumable=True)
            f = self.service.files().create(body=fileMetadata, media_body=media, fields='id, name, parents, mimeType, size, modifiedTime').execute()
            color_logger.success(f"Successfully uploaded file: {fileName} to folder: {parentFolderId}")
            return Response.success(f)
        except Exception as e:
            color_logger.error(f"Error uploading file: {fileName}. Error: {str(e)}")
            return Response.error(f'Error uploading file: {str(e)}')
        
    # Modify files?

    def deleteFiles(self, file_ids):

        color_logger.info(f"Deleting files with IDs: {file_ids}")

        results = []
        for file_id in file_ids:
            try:
                response = self.service.files().delete(fileId=file_id).execute()
                color_logger.success(f"Successfully deleted file with ID: {file_id}")
                results.append(Response.success({'content': response, 'file_id': file_id}))
            except Exception as e:
                color_logger.error(f"Error deleting file with ID: {file_id}. Error: {str(e)}")
                results.append(Response.error({'content': f'Error deleting file: {str(e)}', 'file_id': file_id}))

        color_logger.success(f"Deletion process completed for {len(file_ids)} files.")
        return results  

    def queryFile(self, path, file_name):

        color_logger.info(f"Querying for file: {path}/{file_name}")

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
                            fields="files(id, name, mimeType, size, modifiedTime, parents)",
                        )
                        .execute()
                    )
                    
                    filesResponse = response.get("files")
                    color_logger.info(f'Current path: {filesResponse[0]["name"]}')
                    files.append(filesResponse[0])

                    parentId = files[index]['id']

            except HttpError as error:
                color_logger.error(f"An error occurred. {error}")
                return Response.error(error)
            
            except:
                color_logger.error("Error querying file.")
                return Response.error('Error querying file.')
        
        color_logger.success(f"Successfully queried file: {files[len(files) - 1]}")
        return Response.success(files[len(files) - 1])

    def queryFilesInFolder(self, path):

        color_logger.info(f"Querying for files in: {path}")

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
                            fields="files(id, name, mimeType, size, modifiedTime, parents)",
                        )
                        .execute()
                    )

                    parentID = response['files'][0]['id']

            except HttpError as error:
                color_logger.error(f"An error occurred. {error}")
                return Response.error(error)
        
            except:
                color_logger.error("Error querying files.")
                return Response.error('Error querying files.')
        
        color_logger.success(f"Successfully queried files in: {paths[len(paths) - 1]}")
        return Response.success(response)

    def downloadFile(self, fileId):

        color_logger.info(f"Downloading file with ID: {fileId}")

        try:
            request = self.service.files().get_media(fileId=fileId)
            downloaded_file = io.BytesIO()
            downloader = MediaIoBaseDownload(downloaded_file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                color_logger.info(f"Download {int(status.progress() * 100)}.")

        except HttpError as error:
            color_logger.error(f"An error occurred: {error}")
            return Response.error(error)
        
        except:
            color_logger.error("Error downloading file.")
            return Response.error('Error downloading file.')
        
        color_logger.success("Successfully downloaded file.")
        return Response.success(downloaded_file.getvalue())

    # Download zip?

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

            color_logger.info(f"Generating statements for account: {account}, file: {file_name}")

            # Change path to account

            # TODO SHOULD I USE API OR DRIVE 
            path = 'Personal/Wallet/Statements/BAC/' +  account + '/Sources'
            dictToSend = {'path':path, 'file_name':file_name}
            response = rq.post('http://127.0.0.1:5001' + '/drive/download_file', json=dictToSend)
            if response.status_code != 200:
                raise Exception('Error downloading file.')

            # Get month that the statement is for
            period = file_name.split('.')[0]

            # Download file in plain text
            binaryFile = response.content
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

            # Save to drive as Bytes IO or save cache?
            drivePath = f'Personal/Wallet/Statements/BAC/{account}'
            cachePath = f'cache/statements/processed/{period}.csv'

            # Find processed folder
            response = rq.post('http://127.0.0.1:5001' + '/drive/query_file', json={'path':drivePath, 'file_name':'Processed'})
            if response.status_code != 200:
                raise Exception('Error querying Processed folder.')
            
            processed_folder_id = response.json()['content']['id']

            # Save file to cache
            try:
                df_all.to_csv(cachePath, index=False)
                color_logger.success(f"Successfully saved file {drivePath}/Processed/{period}.csv")
            except Exception as e:
                color_logger.error(f"Error saving file: {str(e)}")
                return Response.error('Error saving file.')
            
            # Upload file to drive
            try:
                response = rq.post('http://127.0.0.1:5001' + '/drive/upload_file_with_path', json={'file_path':cachePath, 'parent_folder_id':processed_folder_id})
                if response.status_code != 200:
                    raise Exception('Error uploading file.')
                color_logger.success(f"Successfully saved file {drivePath}/Processed/{period}.csv")
            except Exception as e:
                color_logger.error(f"Error uploading file: {str(e)}")
                return Response.error('Error uploading file.')
            
            return Response.success(f'Successfully processed {period} financial statements for account: {account}. Saved to {drivePath}/Processed/{period}.csv')

        def parseStatements(self, file_text):

            color_logger.info("Parsing statements")
            rows = file_text.splitlines()
            parsed_csv = csv.reader(rows)
            account_number = None

            rows = []

            write = False
            previous_row = None
            
            for row in parsed_csv:
                if len(row) >  0:

                    if previous_row is not None and len(previous_row) > 0 and previous_row[0] == 'Fecha de Transacción':
                        write = True

                    if row[0] == '':
                        write = False
                    
                    if (write):
                        rows.append(row)

                    if row[0].isdigit():
                        account_number = row[2]

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

            color_logger.success("Successfully parsed statements.")

            return df_statements, account_number

        def getEntries(self, df_statements):
            color_logger.info("Getting entries from statements")
            df_debits = df_statements[df_statements['Credit'].astype(float) == 0].copy()
            color_logger.info("Successfully got debits.")
            df_credits = df_statements[df_statements['Debit'].astype(float) == 0].copy()
            color_logger.success("Successfully got credits.")
            return df_debits, df_credits
        
        def categorizeStatements(self, df_statements):
            color_logger.info("Categorizing statements")

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
                
                color_logger.success("Successfully categorized debits.")

            # Credits             
            else:

                for index, row in df_statements.iterrows():

                    for savings_account in ['960587293', 'SAVINGS']:
                        if savings_account in row['Description']:
                            df_statements.loc[index,'Category'] = 'Savings'

                    for income_source in ['DEP', '1Q', '2Q', 'INCOME']:
                        if income_source in row['Description']:
                            df_statements.loc[index,'Category'] = 'Income'
                
                color_logger.success("Successfully categorized credits.")

            return df_statements

        def manuallyCategorizeStatements(self, df_statements):
            for index, row in df_statements[df_statements['Category'] == ''].iterrows():
                category = input('Enter category for statement:')
                df_statements.loc[index, 'Category'] = category

            return df_statements

class Market:
    def __init__(self):
        color_logger.info("Initializing Markets.")
        self.tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'V']
        color_logger.success("Successfully initialized Markets.")

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

        color_logger.info(f"Retrieved market data for {len(marketData)} tickers")
        return marketData



# Dont care for now
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
        color_logger.info(f"Scraping URL: {url}")
        # Send a request to fetch the HTML content
        response = rq.get(url)
        if response.status_code != 200:
            color_logger.error("Failed to retrieve the web page.")
            return Response.error("Failed to retrieve the web page.")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        color_logger.success("Successfully scraped URL.")
        return soup

from datetime import datetime
import pytz

import ast
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

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import certifi

import time

class laserfocus:
  
    def __init__(self):
        self.url = 'https://laserfocus-api.onrender.com'

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
                except:
                    print('Error saving file.')
                    return {'error':'error'}
                
                print('Processed data.')
                
                return {'status':'success'}

            def parseStatements(self, file_text):

                rows = file_text.splitlines()
                parsed_csv = csv.reader(rows)
                account_number = None

                rows = []

                write = False
                previous_row = None
                
                for row in parsed_csv:
                    if len(row) >  0:
                        print(row)

                        if previous_row is not None and len(previous_row) > 0 and previous_row[0] == 'Fecha de Transacción':
                            write = True

                        if row[0] == '':
                            write = False
                        
                        if (write):
                            rows.append(row)

                        if row[0].isdigit():
                            account_number = row[2]
                        print(account_number)

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

                df_debits = df_statements[df_statements['Credit'].astype(float) == 0].copy()

                df_credits = df_statements[df_statements['Debit'].astype(float) == 0].copy()

                return df_debits, df_credits
            
            def categorizeStatements(self, df_statements):

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

                for index, row in df_statements[df_statements['Category'] == ''].iterrows():
                    print('\n', row)
                    category = input('Enter category for statement:')
                    df_statements.loc[index, 'Category'] = category

                return df_statements

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
            lastWorkingDate = laserfocus.DateAndTime().lastWorkingDate
            lastPrice = self.historicalStocksData[ticker][lastWorkingDate]['Close']
            return lastPrice
        
    class News:

        def __init__(self):
            self.state = 0

        def getSpaceFlightNews(self):
            url = "https://api.spaceflightnewsapi.net/v4/articles/"
            response = rq.get(url)
            news = response.json()
            return {'status':'success', 'content':news}
        
        def scrapeCNNHeadlines(self):

            browser = laserfocus.Browser()
            url = 'https://www.cnn.com'
            soup = browser.scraper(url)

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

    class Home:
        def __init__(self):
            self.state = 0

    class Drive:

        def __init__(self):

            SCOPES = ['https://www.googleapis.com/auth/drive']

            # TODO replace with env
            creds = Credentials.from_authorized_user_file("creds/token.json", SCOPES)
            
            self.service = build("drive", "v3", credentials=creds)

        # Add upload files
        # Add create folder?

        # Modify files?

        # Delete files

        # Remove this?
        def queryForFile(self, path, file_name):

            print(path, '/', file_name)

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
                        print(filesResponse)
                        files.append(filesResponse[0])

                        parentId = files[index]['id']

                except HttpError as error:
                    print(f"An error occurred. {error}")
                    return {'status':'error'}
                
                except:
                    print('Error querying file.')
                    return {'status':'no_data', 'content':None}
            
            return {'content':files[len(files) - 1], 'status':'success'}

        def queryForFiles(self, path):

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
                    print(f"An error occurred. {error}")
                    return {'status':'error'}
            
                except:
                    return {'status':'no_data', 'content':None}
            
            return {'content':response, 'status':'success'}

        def downloadFile(self, fileId):

            try:
                request = self.service.files().get_media(fileId=fileId)
                downloaded_file = io.BytesIO()
                downloader = MediaIoBaseDownload(downloaded_file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}.")

            except HttpError as error:
                print(f"An error occurred: {error}")
                downloaded_file = None
                return ({'status':'error'})
            
            except:
                return {'status':'no_data', 'content':None}
            
            return {'content':downloaded_file.getvalue(), 'status':'success'}

    class Database:

        def __init__(self):

            # Create a new client and connect to the server

            # TODO replace with env
            uri = "mongodb+srv://aguilarcarboni:B5A1OqHHOJ409OH2@owner.bg1trmz.mongodb.net/?retryWrites=true&w=majority&appName=owner"

            self.client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
            print('Initialized client')

        # Replace individual CRUD operations?

        def queryDocumentInCollection(self, database, table, query):

            print('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})

            try:
                query = ast.literal_eval(query)
            except:
                print('Malformed query query.')
                return {'status':'error', 'content':'Malformed query.'}
            
            for key in query:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    query[key] = ObjectId(query[key])
        
            if database not in self.client.list_database_names():
                print('No database with that name found.')
                return {'status':'error', 'content':'No database with that name found.'}
            db = self.client[database]
            
            if table not in database.list_collection_names():
                print('No table with that name found.')
                return {'status':'error', 'content':'No table with that name found.'}
            
            tb = db[table]
            
            entry = tb.find_one(query)
            
            if entry is not None:
                print('Successfully queried entry.', {'content':entry})
                return {'status':'success', 'content':entry}
            else:
                print('Entry not found.')
                return {'status':'no_data', 'content':None}
        
        def queryDocumentsInCollection(self, database, table, query):

            print('Querying entries in table in database.', {'database':database, 'table':table, 'query':query})

            try:
                query = ast.literal_eval(query)
            except:
                print('Malformed query query.')
                return {'status':'error', 'content':'Malformed query.'}
            
            for key in query:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    query[key] = ObjectId(query[key])
        
            if database not in self.client.list_database_names():
                print('No database with that name found.')
                return {'status':'error', 'content':'No database with that name found.'}
            
            db = self.client[database]
            
            if table not in db.list_collection_names():
                print('No table with that name found.')
                return {'status':'error', 'content':'No table with that name found.'}
            
            tb = db[table]
            
            entry = tb.find(query)
            
            if entry is not None:
                print('Successfully queried entry.', {'content':entry})
                return {'status':'success', 'content':entry}
            else:
                print('Entry not found.')
                return {'status':'no_data', 'content':None}

        def updateDocumentInCollection(self, database, table, data, query):

            print('Updating entry in table in database.', {'database':database, 'table':table, 'data':data, 'query':query})
            
            try:
                query = ast.literal_eval(query)
            except:
                print('Malformed query.')
                return {'status':'error', 'content':'Malformed query.'}
            
            for key in query:
                if 'id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    query[key] = ObjectId(query[key])

            try:
                data = ast.literal_eval(data)
            except:
                print('Malformed data.')
                return {'status':'error', 'content':'Malformed data.'}
            
            for key in data:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    data[key] = ObjectId(data[key])

            collection = self.client[database]

            collection = collection[table]
            try:
                entry = collection.update_one(query, {
                    '$set': data
                })
            except:
                print('Error updating document.')
                return {'error':'Error updating document.'}
            
            print('Successfully updated entry.', {'document':entry})
            return {'status':'success', 'content':entry}

        def insertDocumentToCollection(self, database, table, data, context):

            print('Inserting entry to table in Database.', {'database':database, 'table':table, 'data':data})
            try:
                data = ast.literal_eval(data)
            except:
                print('Malformed data.')
                return {'status':'error', 'content':'Malformed data.'}
            
            for key in data:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    data[key] = ObjectId(data[key])

            for key in context:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    context[key] = ObjectId(context[key])

            db = self.client[database]
            tb = db[table]

            try:
                insertedData = tb.insert_one(data)
            except:
                print('Error inserting entry.')
                return {'status':'error'}

            print('Successfully inserted entry.')
            insertedId = insertedData.inserted_id

            print('Adding dependencies that relate to entry.')

            dependencies = self.insertDependencies(table, data, ObjectId(insertedId), context)
        
            return {'status':'success', 'content':{'data':str(insertedId), 'dependencies':dependencies}}

        def deleteDocumentInCollection(self, database, table, query):

            print('Deleting entry in table in Database.', {'database':database, 'table':table, 'query':query})
            query = ast.literal_eval(query)

            for key in query:
                if 'id' in key or 'Id' in key:
                    print(f'Converting id {key} to ObjectId.')
                    query[key] = ObjectId(query[key])

            db = self.client[database]
            tb = db[table]

            try:
                deletedData = tb.find_one_and_delete(query)
            except:
                print('Error deleting entry.')
                return {'status':'error'}

            print('Successfully deleted entry.')
            deletedId = deletedData['_id']
            print(deletedId, type(deletedId))

            print('Deleting dependencies that relate to entry.')
            dependencies = self.deleteDependencies(table, deletedId)

            return {'status':'success', 'content':{'data':str(deletedData), 'dependencies':dependencies}}

        def insertDependencies(self, table, data, insertedId, context):

            dependencies = {}
            match table:
                case 'user':
                    
                    result = self.insertDocumentToCollection('spaces', 'space', '{"name":"' + str(data['name']) + 's Space"}', {'userId':str(insertedId)})
                    print(result['content'])

                    dependencies = {'space':result['content']['data']}

                    for key in result['content']['dependencies']:
                        dependencies[key] = result['content']['dependencies'][key]

                    print(dependencies)

                case 'event':
                    
                    # Insert space event relationship
                    result = self.insertDocumentToCollection('spaces', 'space-event', '{"eventId":"' + str(insertedId) + '", "spaceId":"'+ str(context['spaceId']) + '"}', {})
                    print(result['content'])

                    dependencies = {'space-event':result['content']['data']}

                    for key in result['content']['dependencies']:
                        dependencies[key] = result['content']['dependencies'][key]

                case 'space':

                    # Insert user space relationship
                    result = self.insertDocumentToCollection('users', 'user-space', '{"userId":"' + str(context['userId']) + '", "spaceId":"'+ str(insertedId) + '"}', {})
                    print(result['content'])

                    dependencies = {'user-space':result['content']['data']}

                    for key in result['content']['dependencies']:
                        dependencies[key] = result['content']['dependencies'][key]

                case _:
                    pass

            return dependencies

        def deleteDependencies(self, table, deletedId):

            dependencies = {}
            match table:
                case 'user':

                    result = self.deleteDocumentInCollection('users', 'user-space', '{"userId":"' + str(deletedId) + '}')
                    print(result['content'])

                    dependencies = {'space':result['content']['data']}

                    for key in result['content']['dependencies']:
                        dependencies[key] = result['content']['dependencies'][key]

                    print(dependencies)

                case 'space':
                    pass

                case 'user-space':
                    
                    result = self.deleteDocumentInCollection('spaces', 'space', '{"spaceId":"' + str(deletedId) + '}')
                    print(result['content'])

                    dependencies = {'space':result['content']['data']}

                    for key in result['content']['dependencies']:
                        dependencies[key] = result['content']['dependencies'][key]

                    print(dependencies)

            return dependencies

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
            # Send a request to fetch the HTML content
            response = rq.get(url)
            if response.status_code != 200:
                print("Failed to retrieve the web page.")
                return

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return soup

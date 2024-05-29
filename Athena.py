from datetime import datetime
import requests as rq
import math
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime
import pytz

class Athena:       
    class Brain:
        def __init__(self):
            self.API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
            self.headers = {"Authorization": "Bearer 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"}

        def ask(self, payload):
            self.response = rq.post(self.API_URL, headers=self.headers, json={"inputs": payload})
            return self.response.json()

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
            self.weatherURL = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=eb19583dcac353340bf0b6ba9becd965"
            self.response = rq.get(self.weatherURL)
            self.data = self.response.json()
            self.temperature = self.getTemperature()

        def getTemperature(self):
            currentTemp = self.data['main']['temp']
            currentTemp -= 273.15
            currentTemp = math.floor(currentTemp)
            return currentTemp
        
    class Market:
        def __init__(self):
            self.data = self.getMarketData()

        def getMarketData(self):
            self.tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT']

            self.marketData = {}

            for ticker in self.tickers:
                
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
            self.lastPrice = self.getMarketData()[ticker]['20240523']['Close']
            return self.lastPrice
        
    class News:
        def __init__(self):
            self.state = 0
            
    class Calendar:
        def __init__(self):
            self.state = 0
            
    class Sports:
        def __init__(self):
            self.state = 0

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
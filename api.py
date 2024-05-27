from datetime import datetime
import yfinance as yf

from flask import Flask
from flask_cors import CORS

from marsFunctions import getImages, getManifestData, getSol, getWaypoints
from Athena import Athena

# Market Data
def getMarketData():
    tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT']

    marketData = {}

    for ticker in tickers:
        
        tickerData = yf.Ticker(ticker)

        end_date = datetime.now().strftime('%Y-%m-%d')

        # get all stock info
        tickerData = tickerData.history(start='2024-03-15', end=end_date)

        tickerHistory = {}
        prevDate = '2024-03-15'

        for date in (tickerData.index):
            date = str('%04d' % date.year) + '-' + str('%02d' % date.month) + '-' + str('%02d' % date.day)
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
marketData = getMarketData()
print(marketData)

# Mars Data
def getMarsData():
    manifestUrl = 'https://api.nasa.gov/mars-photos/api/v1/manifests/perseverance/?api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
    manifest = getManifestData(manifestUrl)

    sol = getSol(manifest)

    imagesUrl = 'https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?sol='+ str(sol) + '&api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
    waypointsUrl = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'

    images = getImages(imagesUrl)
    coordinates = getWaypoints(waypointsUrl)

    marsData = {
        'images': images,
        'coords': coordinates
    }

    return marsData
marsData = getMarsData()
print(marsData)

lat = 9.9382
lon = -84.1426

Athena = Athena()
DateAndTime = Athena.DateAndTime()
Weather = Athena.Weather(lat,lon)
Market = Athena.Market()

athenaData = [DateAndTime.getCurrentDate(), DateAndTime.getCurrentTime(),  Weather.getTemperature(), round(Market.data['AAPL']['2024-05-24']['Close'], 3)]

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def root():
    return 'Welcome to the laserfocus API'

@app.route("/market")
def market():
    return marketData

@app.route("/mars")
def mars():
    return marsData

@app.route("/athena")
def athena():
    return athenaData
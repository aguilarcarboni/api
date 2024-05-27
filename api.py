from flask import Flask
from flask_cors import CORS

from marsFunctions import getImages, getManifestData, getSol, getWaypoints
from Athena import Athena

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

athenaData = [DateAndTime.getCurrentDate(), DateAndTime.getCurrentTime(),  Weather.getTemperature(), {'AAPL':round(Market.data['AAPL']['2024-05-24']['Close'], 3)}]
print(athenaData)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def root():
    return 'Welcome to the laserfocus API'

@app.route("/mars")
def mars():
    return marsData

@app.route("/athena")
def athena():
    return athenaData
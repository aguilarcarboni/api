from flask import Flask
from flask_cors import CORS

from marsFunctions import getMarsData
from Athena import Athena

# Mars Data
marsData = getMarsData()
print(marsData)

lat = 9.9382
lon = -84.1426

Athena = Athena()
DateAndTime = Athena.DateAndTime()
Weather = Athena.Weather(lat,lon)
Market = Athena.Market()

athenaData = {
    'date': DateAndTime.getCurrentDate(), 
    'time': DateAndTime.getCurrentTime(),  
    'weather': Weather.getTemperature(), 
    'market': Market.data
}
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
from flask import Flask
from flask_cors import CORS

from Athena import Athena

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

Athena = Athena()

@app.route("/")
def root():
    return 'any path to success starts with laserfocus.'

@app.route("/athena")
def athena():
    athenaData = {
        'date': Athena.DateAndTime().currentDate, 
        'time': Athena.DateAndTime().currentTime,
        'currentTemp': Athena.Weather(9.9382,-84.1426).currentTemp,
    }
    return athenaData

@app.route("/athena/market")
def market():
    marketData = {
        'stocks':{
            'AAPL': Athena.Market().getLastPrice('AAPL'),
            'SPY': Athena.Market().getLastPrice('SPY')
        },
        'historical':Athena.Market().data
    }
    return marketData

@app.route("/athena/mars")
def mars():
    marsData = Athena.Explorer().Mars().data
    return marsData

@app.route("/athena/brain")
def brain():
    brainData = Athena.Brain().ask("Tell me more about Baseball")
    return brainData

@app.route("/athena/news")
def news():
    newsData = {
        'general':Athena.News().getNews(), 
        'space':Athena.News().getSpaceFlightNews()
    }
    return newsData

@app.route("/athena/weather")
def weather():
    weatherData = {
        'forecast':Athena.Weather(9.9382,-84.1426).forecast, 
        'uv':Athena.Weather(9.9382,-84.1426).uv
    }
    return weatherData

@app.route("/athena/sports")
def sports():
    sportsData = Athena.Sports().data
    return sportsData

debug = False
if debug:

    if __name__ == "__main__": 
        app.run(debug=True) 
        
    print('Service live.')
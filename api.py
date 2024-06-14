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
    News = Athena.News()
    newsData = {
        'general':News.getNews(), 
        'space':News.getSpaceFlightNews()
    }
    return newsData

@app.route("/athena/weather")
def weather():
    Weather = Athena.Weather(9.939085748069655, -83.98204884169583)
    weatherData = {
        'forecast':Weather.forecast, 
        'currentWeather': Weather.currentWeather,
    }
    return weatherData

@app.route("/athena/sports")
def sports():
    sportsData = {}
    return sportsData

debug = False
if debug:

    if __name__ == "__main__": 
        app.run(debug=True) 
        
    print('Service live.')
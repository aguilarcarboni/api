from flask import Flask, request, jsonify
from flask_cors import CORS

from firestore_api_helpers import initializeFirebase
from Athena import Athena

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = initializeFirebase()

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
    tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT']
    Market = Athena.Market(tickers)
    marketData = {
        'stocks':{
            'last':{
            },
            'historical': Market.historicalStocksData
        },
    }

    for ticker in tickers:
        marketData['stocks']['last'][ticker] = Market.getLastPrice(ticker)

    return marketData

@app.route("/athena/mars")
def mars():
    marsData = Athena.Explorer().Mars().data
    return marsData

# Brain
@app.route("/athena/brain")
def brain():
    return "QUOD OBSTAT VIAE FIT VIA"

@app.route('/athena/brain/ask', methods=['POST'])
async def ask_athena():
    input_json = request.get_json(force=True)
    Brain = Athena.Brain()
    response = await Brain.ask(input_json['message'])
    return jsonify(response)

# News
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

debug = True
if debug:

    if __name__ == "__main__": 
        app.run(debug=True)
        
    print('Service live.')
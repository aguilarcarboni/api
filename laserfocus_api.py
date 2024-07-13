from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

from io import BytesIO

from datetime import datetime

from laserfocus import laserfocus

from bson import json_util
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

laserfocus = laserfocus()

@app.route("/")
def root():
    data = {
        'title':'any path to success starts with laserfocus.',
        'date': laserfocus.DateAndTime().currentDate, 
        'time': laserfocus.DateAndTime().currentTime,
    }
    return data

@app.route("/market")
def market():
    tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'AMZN', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'V']
    Market = laserfocus.Market(tickers)
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

# News
@app.route("/news")
def news():
    News = laserfocus.News()
    newsData = {
        'general':News.getNews(), 
        'space':News.getSpaceFlightNews()
    }
    return newsData

# Weather
@app.route("/weather")
def weather():
    Weather = laserfocus.Weather(9.939085748069655, -83.98204884169583)
    weatherData = {
        'forecast':Weather.forecast, 
        'currentWeather': Weather.currentWeather,
    }
    return weatherData

# Sports
@app.route("/sports")
def sports():
    sportsData = {}
    return sportsData

# Explorer
@app.route("/explorer/mars")
def mars():
    marsData = laserfocus.Explorer().Mars().data
    return marsData

# Drive
@app.route('/drive/query', methods=['POST'])
async def drive():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])

    fileContent = Drive.downloadFile(response['id'])
    f = BytesIO(fileContent)

    return send_file(f, mimetype="text/plain")

# Database
@app.route('/mongo/query', methods=['POST'])
async def mongo_query():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.queryDocumentInCollection(input_json['query'],input_json['path'])
    return json.loads(json_util.dumps(response))

@app.route('/mongo/insert', methods=['POST'])
async def mongo_insert():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.insertDocumentToCollection(input_json['data'], input_json['path'])
    return {}

@app.route('/mongo/update', methods=['POST'])
async def mongo_update():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.updateDocumentInCollection(input_json['data'], input_json['query'],input_json['path'])
    return {}

# Wallet
@app.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    # Athena input
    input_json = request.get_json(force=True)
    BAC = laserfocus.Wallet.BAC()

    # TODO cambiar a file object
    f = input_json['file_text']

    df_statements = BAC.parseStatements(f)
    df_debits, df_credits = BAC.getEntries(df_statements)

    df_debits = BAC.categorizeStatements(df_debits)
    df_credits = BAC.categorizeStatements(df_credits)

    # Save to drive
    # Output path: Personal/Wallet/Statements/{Bank}/{AccountNumber}
    # Output file name: MMYYYY.csv
    time = datetime.now()
    time = time.strftime('%d%M%Y%H%M%S')
    df_debits.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/Tests/{time}.csv')

    print('Processed data.')
    return {'path':f'Personal/Wallet/Statements/Tests/{time}'}

debug = True
if debug:

    if __name__ == "__main__": 
        app.run(debug=True)
        
    print('Service live.')
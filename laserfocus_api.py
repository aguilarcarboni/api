from flask import Flask, request, send_file
from flask_cors import CORS

from io import BytesIO

from laserfocus import laserfocus

from bson import json_util
import json

import time

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
    newsData = News.scrapeCNNHeadlines()
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
@app.route('/drive/query_files', methods=['POST'])
async def drive_query_many():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()
    response = Drive.queryForFiles(input_json['path'])
    return response

@app.route('/drive/query_file', methods=['POST'])
async def drive_query_file():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()

    if input_json['file_name'].endswith('.xlsx') or input_json['file_name'].endswith('.csv'):
        mimetype="text/plain"
    else:
        return {'status':'error', 'content':'File type not supported.'}

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])
    response = Drive.downloadFile(response['content']['id'])
    f = BytesIO(response['content'])

    return send_file(f, mimetype=mimetype)

@app.route('/drive/query_id', methods=['POST'])
async def drive_query_id():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])

    return response

# TODO ADD UPLOAD FILE

# Database
# TODO MAYBE REMOVE THIS
@app.route('/database/query', methods=['POST'])
async def mongo_query():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.queryDocumentInCollection(input_json['database'], input_json['table'], input_json['query'])
    return json.loads(json_util.dumps(response))

@app.route('/database/query_many', methods=['POST'])
async def mongo_query_many():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.queryDocumentsInCollection(input_json['database'], input_json['table'], input_json['query'])
    return json.loads(json_util.dumps(response))

# TODO THIS NEEDS CHECKING
@app.route('/database/update', methods=['POST'])
async def mongo_update():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.updateDocumentInCollection(input_json['database'], input_json['table'], input_json['data'], input_json['query'])
    return json.loads(json_util.dumps(response))

# TODO CREATE BULK INSERTS
@app.route('/database/insert', methods=['POST'])
async def mongo_insert():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.insertDocumentToCollection(input_json['database'], input_json['table'], input_json['data'], input_json['context'])
    return response

@app.route('/database/delete', methods=['POST'])
async def mongo_delete():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.deleteDocumentInCollection(input_json['database'], input_json['table'], input_json['query'])
    return response

# Wallet
@app.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    # Is document given?

    BAC = laserfocus.Wallet.BAC()

    # Query drive for document
    input_json = request.get_json(force=True)

    # Acccccc
    account = input_json['account']
    file_name = input_json['file_name']

    response = BAC.generateStatements(account, file_name)
    return response

debug = True
if debug:

    if __name__ == "__main__": 
        app.run(debug=True)
        
    print('Service live.')
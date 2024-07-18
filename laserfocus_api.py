from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

from io import BytesIO

from datetime import datetime

from laserfocus import laserfocus

from bson import json_util
import json

import requests as rq

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

laserfocus = laserfocus()

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

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
@app.route('/drive/query_file', methods=['POST'])
async def drive_query_file():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])
    fileContent = Drive.downloadFile(response['id'])

    f = BytesIO(fileContent)

    return send_file(f, mimetype="text/plain")

@app.route('/drive/query_id', methods=['POST'])
async def drive_query_id():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive()

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])
    print(response)

    return response

# Database
@app.route('/database/query', methods=['POST'])
async def mongo_query():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.queryDocumentInCollection(input_json['database'], input_json['table'], input_json['query'],)
    return json.loads(json_util.dumps(response))

@app.route('/database/update', methods=['POST'])
async def mongo_update():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.updateDocumentInCollection(input_json['database'], input_json['table'], input_json['data'], input_json['query'])
    return {}

@app.route('/database/insert', methods=['POST'])
async def mongo_insert():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.insertDocumentToCollection(input_json['database'], input_json['table'], input_json['data'])
    return {}

# Wallet
@app.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    # Is document given?

    BAC = laserfocus.Wallet.BAC()

    # Query drive for document
    input_json = request.get_json(force=True)
    path = 'Personal/Wallet/Statements/BAC/Sources/' +  input_json['path']
    dictToSend = {'path':path, 'file_name':input_json['file_name']}
    res = rq.post(url + '/drive/query', json=dictToSend)

    # Download file in plain text
    binaryFile = res.content
    file_text = binaryFile.decode('latin1')

    df_statements, account_number = BAC.parseStatements(file_text)
    account_number = account_number.strip()
    print(account_number)

    accounts = [{'id':'CR83010200009295665295', 'name':'Cash'}]

    # Query database
    for account in accounts:
        if account['id'] == account_number and account['name'] == input_json['path']:
            account = account['name']

    # Get account number

    df_debits, df_credits = BAC.getEntries(df_statements)

    df_debits = BAC.categorizeStatements(df_debits)
    df_credits = BAC.categorizeStatements(df_credits)

    # Save to drive
    # Output path: Personal/Wallet/Statements/{Bank}/{AccountNumber}
    # Output file name: MMYYYY.csv

    try:
        df_debits.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/Processed/{account}/debits_{laserfocus.DateAndTime().currentDateTimeString}.csv')
        df_credits.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/Processed/{account}/credits_{laserfocus.DateAndTime().currentDateTimeString}.csv')
    except:
        return {'error':'error'}

    print('Processed data.')
    return {'account':account_number}

debug = True
if debug:

    if __name__ == "__main__": 
        app.run(debug=True)
        
    print('Service live.')
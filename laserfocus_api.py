from flask import Flask, request, send_file
from flask_cors import CORS

import pandas as pd

from io import BytesIO

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
@app.route('/drive/query_files', methods=['POST'])
async def drive_query_files_in_folder():

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

# Database
@app.route('/database/query', methods=['POST'])
async def mongo_query():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.queryDocumentInCollection(input_json['database'], input_json['table'], input_json['query'])
    return json.loads(json_util.dumps(response))

@app.route('/database/update', methods=['POST'])
async def mongo_update():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.updateDocumentInCollection(input_json['database'], input_json['table'], input_json['data'], input_json['query'])
    return response

@app.route('/database/insert', methods=['POST'])
async def mongo_insert():
    # Athena input
    input_json = request.get_json(force=True)
    Mongo = laserfocus.Database()
    response = Mongo.insertDocumentToCollection(input_json['database'], input_json['table'], input_json['data'])
    return response

# Wallet
@app.route("/wallet/bac/generateStatements", methods=['POST'])
def bac_generate_statements():

    # Is document given?

    BAC = laserfocus.Wallet.BAC()

    # Query drive for document
    input_json = request.get_json(force=True)
    path = 'Personal/Wallet/Statements/BAC/' +  input_json['path'] + '/Sources'
    dictToSend = {'path':path, 'file_name':input_json['file_name']}
    res = rq.post(url + '/drive/query_file', json=dictToSend)

    period = input_json['file_name'].split('.')[0]

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

    df_all = pd.concat([df_debits, df_credits])
    df_all['Total'] = df_all['Credit'].astype(float) - df_all['Debit'].astype(float)
    df_all = df_all.sort_values(by='Date')

    # Save to drive
    # Output path: Personal/Wallet/Statements/{Bank}/{AccountNumber}
    # /Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Processed
    # Output file name: MMYYYY.csv

    print(account, period)

    try:
        df_debits.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/{account}/Processed/debits_{period}.csv')
        df_credits.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/{account}/Processed/credits_{period}.csv')
        df_all.to_csv(f'/Users/andres/Google Drive/My Drive/Personal/Wallet/Statements/BAC/{account}/Processed/{period}.csv')

    except:
        return {'error':'error'}

    print('Processed data.')
    return {'account':account_number}

debug = True
if debug:

    if __name__ == "__main__": 
        app.run(debug=True)
        
    print('Service live.')
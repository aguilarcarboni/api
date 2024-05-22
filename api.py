import yfinance as yf
from datetime import datetime
from flask import Flask
from flask_cors import CORS, cross_origin

#Main
tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT']

data = {}

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

    data[ticker] = tickerHistory

for ticker in data:
    for date in data[ticker]:
        data[ticker][date]['Change $'] = data[ticker][date]['Close'] - data[ticker][prevDate]['Close']
        data[ticker][date]['Change %'] = (data[ticker][date]['Close'] - data[ticker][prevDate]['Close'])/data[ticker][date]['Close'] * 100
        prevDate = date

print(data)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@cross_origin()

@app.route("/")
def root():
    return data

@app.route("/market")
def market():
    return data
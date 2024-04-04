import yfinance as yf
from datetime import datetime
from flask import Flask
from flask_cors import CORS, cross_origin

#Main
tickers = ['SPY', 'QQQ', 'DIA', 'NVDA', 'AAPL']

data = {}

for ticker in tickers:
    
    tickerData = yf.Ticker(ticker)

    end_date = datetime.now().strftime('%Y-%m-%d')

    # get all stock info
    tickerData = tickerData.history(start='2024-03-15', end=end_date)

    tickerHistory = {}

    for date in (tickerData.index):
        date = str(date.month) + '/' + str(date.day) + '/' + str(date.year)
        tickerHistory[date] = {}
        for cat in tickerData.iloc[0,:].index:
            info = tickerData.iloc[0,:][cat]
            tickerHistory[date][cat] = info

    data[ticker] = tickerHistory

print(data)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def root():
    return data
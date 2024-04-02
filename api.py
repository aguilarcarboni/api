import yfinance as yf
from flask import Flask
from flask_cors import CORS, cross_origin

#Main
ticker = 'AAPL'

tickerData = yf.Ticker(ticker)

# get all stock info
results = tickerData.info

data = {
    ticker:results
}

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def root():
    return data
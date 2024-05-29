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
        'weather': Athena.Weather(9.9382,-84.1426).temperature, 
    }
    return athenaData

@app.route("/athena/market")
def market():
    marketData = {
        'AAPL': Athena.Market().getLastPrice('AAPL'),
        'SPY': Athena.Market().getLastPrice('SPY')
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

"""
print('Service live.')

if __name__ == "__main__": 
    app.run(debug=True) 
"""
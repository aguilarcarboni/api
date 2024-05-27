from datetime import datetime
import requests as rq
import math
import yfinance as yf

class Athena:       
    class DateAndTime:
        def __init__(self):
            self.currentDateTime = datetime.now()
        def getCurrentTime(self):
            currentTime = self.currentDateTime.strftime("%I:%M%p")
            return currentTime
        def getCurrentDate(self):
            currentDate = self.currentDateTime.strftime("%A %B %d %Y")
            return currentDate
        def getTimeOfDay(self):
            hourTime = self.currentDateTime.hour
            if (hourTime > 5 and hourTime < 12):
                timeOfDay = 'morning'
            elif (hourTime > 12 and hourTime < 18):
                timeOfDay = 'afternoon'
            else:
                timeOfDay = 'night'
            return timeOfDay

    class Weather:
        def __init__(self,lat,lon):
            self.weatherURL = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=eb19583dcac353340bf0b6ba9becd965"
            self.response = rq.get(self.weatherURL)
            self.data = self.response.json()
        def getTemperature(self):
            currentTemp = self.data['main']['temp']
            currentTemp -= 273.15
            currentTemp = math.floor(currentTemp)
            return currentTemp
        
    class Market:
        def __init__(self):
            self.data = self.getMarketData()

        def getMarketData(self):
            self.tickers = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT']

            self.marketData = {}

            for ticker in self.tickers:
                
                self.tickerData = yf.Ticker(ticker)

                self.end_date = datetime.now().strftime('%Y-%m-%d')

                # get all stock info
                self.tickerData = self.tickerData.history(start='2024-03-15', end=self.end_date)

                self.tickerHistory = {}
                self.prevDate = '2024-03-15'

                for date in (self.tickerData.index):
                    date = str('%04d' % date.year) + '-' + str('%02d' % date.month) + '-' + str('%02d' % date.day)
                    self.tickerHistory[date] = {}
                    for cat in self.tickerData.iloc[0,:].index:
                        info = self.tickerData.loc[date,:][cat]
                        self.tickerHistory[date][cat] = info

                self.marketData[ticker] = self.tickerHistory

            for ticker in self.marketData:
                for date in self.marketData[ticker]:
                    self.marketData[ticker][date]['Change $'] = self.marketData[ticker][date]['Close'] - self.marketData[ticker][self.prevDate]['Close']
                    self.marketData[ticker][date]['Change %'] = (self.marketData[ticker][date]['Close'] - self.marketData[ticker][self.prevDate]['Close'])/self.marketData[ticker][date]['Close'] * 100
                    self.prevDate = date

            return self.marketData

    class News:
        def __init__(self):
            self.state = 0
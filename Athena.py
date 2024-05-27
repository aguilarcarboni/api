import datetime as dt
import requests as rq
import math

class Athena:
                
    class DateAndTime:
        def __init__(self):
            self.currentDateTime = dt.datetime.now()
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
            self.dataURL = 'https://laserfocus-api.onrender.com/market'
            self.response = rq.get(self.dataURL)
            self.data = self.response.json()

    class News:
        def __init__(self):
            self.state = 0
import datetime as dt
import requests as rq
import math
import speech_recognition as sr
import pyttsx3 as tts

class Athena:

    class Ears:

        def __init__(self):
            self.recognizer = sr.Recognizer()
            self.message = ''
            
        def listen(self):
            try:
                with sr.Microphone() as mic:
                    print("Listening...")
                    audio = self.recognizer.listen(mic,3)
                    return audio
            except:
                pass

        def getMessage(self, audio):
            text = self.recognizer.recognize_google(audio, language='en-IN',show_all=True)
            if type(text) is dict:
                self.message = text['alternative'][0]['transcript']
            print(self.message)
            return self.message

    class Mouth:

        def __init__(self):
            self.mouth = tts.init()
            self.response = ''

        def talk(self,message):
            self.response = ''
            if message == '0':
                self.response = "Hey, I'm Athena"
            if ('what time is it') in message: # language analysis
                self.response = Athena.DateAndTime.getCurrentTime()
            print(self.response)
            self.mouth.say(self.response)
            self.mouth.runAndWait()
            return self.response
                
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
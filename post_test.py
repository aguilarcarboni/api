#make a POST request
import requests

dictToSend = {'message':"What is the next step in connecting you, Athena, to my Google API?"}

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

res = requests.post(url + '/athena/brain/ask', json=dictToSend)
dictFromServer = res.json()
print(dictFromServer)
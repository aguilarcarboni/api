#make a POST request
import requests as rq

debug = False
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

print('Welcome to Athena (A Thourougly Helpful Everyday Natural Asistant)')
print('Ask her anything or press enter to say goodbye to Athena.')

message = ''
while True:
    message = input('User:')

    if message == '':
        exit('Exiting program...')

    dictToSend = {'message':message}

    res = rq.post(url + '/athena/brain/ask', json=dictToSend)
    dictFromServer = res.json()
    print('Athena:', dictFromServer)
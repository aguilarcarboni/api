#make a POST request
import requests
dictToSend = {'message':'what is 9 + 10?'}
res = requests.post('http://127.0.0.1:5000/athena/brain/ask', json=dictToSend)
dictFromServer = res.json()
print(dictFromServer)
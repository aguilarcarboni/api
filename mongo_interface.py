#make a POST request
import requests as rq

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

print('Find any file in your drive.')

path = input('Path:')
query = input('File name:')
data = input('Data:')

queryDict = {'path':path, 'query':query}
updateDict = {'data':data,'path':path, 'query':query}
insertDict = {'data':data, 'path':path}

res = rq.post(url + '/athena/mongo/update', json=updateDict)

print(res)
dictFromServer = res.json()
print('Athena:', dictFromServer)
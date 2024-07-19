#make a POST request
import requests as rq
import pandas as pd
from io import BytesIO

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

print('Find any file in your drive.')

path = input('Path:')
file_name = input('File name:')

dictToSend = {'path':path, 'file_name':file_name}

res = rq.post(url + '/drive/query_file', json=dictToSend)
print(res, res.content)

df = pd.read_csv(BytesIO(res.content), encoding='latin1')
print(df)

"""
dictFromServer = res.json()
print('Athena:', dictFromServer)
"""
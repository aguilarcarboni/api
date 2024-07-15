#make a POST request
import requests as rq
from io import BytesIO
import csv

import pandas as pd

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'

print('Generate your monthly statements.')

path = input('Path:')
file_name = input('File name:')

dictToSend = {'path':path, 'file_name':file_name}
res = rq.post(url + '/wallet/bac/generateStatements', json=dictToSend)

print('Successfully parsed transactions. Saved at:', res.json()['path'])
#make a POST request
import requests as rq
import pandas as pd
from io import BytesIO, StringIO



#make a POST request
import requests as rq

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'


print('Find any file in your drive.')
mode = input('Enter mode:\n1. Query and download file\n2. Query file by ID\n3. Query files in folder\n')

path = input('Path:')

match mode:

    case '1':
        file_name = input('File name:')

        dictToSend = {'path':path, 'file_name':file_name}
        res = rq.post(url + '/drive/query_file', json=dictToSend)

        if file_name.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(res.content))
            dictFromServer = df.to_dict(orient='records')
        else:
            dictFromServer = res.json()

    case '2':
        file_name = input('File name:')

        print('Query any file in a table in Drive.')

        dictToSend = {'path':path, 'file_name':file_name}
        res = rq.post(url + '/drive/query_id', json=dictToSend)
        dictFromServer = res.json()

    case '3':

        print('Query all files in a folder in Drive.')
        dictToSend = {'path':path}
        res = rq.post(url + '/drive/query_files', json=dictToSend)
        dictFromServer = res.json()

print('API Response:', dictFromServer)
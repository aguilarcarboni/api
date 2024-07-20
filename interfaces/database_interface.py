#make a POST request
import requests as rq

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'


mode = input('Enter mode:\n1. Query\n2. Update\n3. Insert\n')
database = input('Database:')
table = input('Table:')

dictToSend = {}

match mode:

    case '1':
        print('Query any entry in a table in the database.')

        key = input('Key:')
        value = input('Value:')
        query = '{' + f'"{key}":"{value}"' + '}'

        dictToSend = {'database':database, 'table':table, 'query':query}

        res = rq.post(url + '/database/query', json=dictToSend)

    case '2':
        print('Update any entry in a table in the database.')

        key = input('Key:')
        value = input('Value:')
        query = '{' + f'"{key}":"{value}"' + '}'

        data = input('Data:')

        dictToSend = {'database':database, 'table':table, 'data':data, 'query':query}

        res = rq.post(url + '/database/update', json=dictToSend)

    case '3':
        print('Insert any entry (document) in your database.')

        data = input('Data:')

        dictToSend = {'database':database, 'table':table, 'data':data}

        res = rq.post(url + '/database/insert', json=dictToSend)

dictFromServer = res.json()
print('API Response:', dictFromServer)
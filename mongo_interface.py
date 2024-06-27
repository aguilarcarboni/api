#make a POST request
import requests as rq

debug = True
if debug:
    url = 'http://127.0.0.1:5000'
else:
    url = 'https://laserfocus-api.onrender.com'


mode = input('Enter mode:\n1. Query\n2. Update\n3. Insert\n')
path = input('Path:')

dictToSend = {}

match mode:

    case '1':
        print('Query any entry (document) in your database.')

        query = input('Query:')
        dictToSend = {'path':path, 'query':query}

        res = rq.post(url + '/athena/mongo/query', json=dictToSend)

    case '2':
        print('Update any entry (document) in your database.')

        query = input('Query:')
        data = input('Data:')

        dictToSend = {'data':data,'path':path, 'query':query}

        res = rq.post(url + '/athena/mongo/update', json=dictToSend)

    case '3':
        print('Insert any entry (document) in your database.')

        data = input('Data:')

        dictToSend = {'data':data, 'path':path}

        res = rq.post(url + '/athena/mongo/insert', json=dictToSend)



print(res)
dictFromServer = res.json()
print('Athena:', dictFromServer)
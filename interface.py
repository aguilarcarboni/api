import requests as rq
import pandas as pd
from io import BytesIO
import ast

def walletInterface():

    print('Wallet Interface')
    print('1. Generate your monthly statements.\n')
    choice = input(message)

    match choice:

        case '1':
            
            print('Generate your monthly statements.')
            account = input('Account:')
            file_name = input('File name:')

            dictToSend = {'account': account, 'file_name':file_name}
            res = rq.post(url + '/wallet/bac/generateStatements', json=dictToSend)
            dictFromServer = res.json()

    print('API Response:', dictFromServer)
    return dictFromServer

def driveInterface():

    print('Drive Interface')
    print('1. Query and download file\n2. Query file by ID\n3. Query files in folder\n')
    choice = input(message)

    match choice:

        case '1':

            print('Query and download any file in Drive.')
            path = input('Path:')
            file_name = input('File name:')

            dictToSend = {'path':path, 'file_name':file_name}
            res = rq.post(url + '/drive/query_file', json=dictToSend)

            if file_name.endswith('.xlsx') or file_name.endswith('.csv'):
                df = pd.read_excel(BytesIO(res.content))
                dictFromServer = df.to_dict(orient='records')
            else:
                dictFromServer = res.json()

        case '2':

            print('Query any file ID in Drive.')
            path = input('Path:')
            file_name = input('File name:')

            dictToSend = {'path':path, 'file_name':file_name}
            res = rq.post(url + '/drive/query_id', json=dictToSend)
            dictFromServer = res.json()

        case '3':

            print('Query all files in a folder in Drive.')
            path = input('Path:')

            dictToSend = {'path':path}
            res = rq.post(url + '/drive/query_files', json=dictToSend)
            dictFromServer = res.json()
        
    return dictFromServer

def databaseInterface():

    print('Database Interface')
    print('1. Query\n2. Update\n3. Insert\n4. Delete\n')
    choice = input(message)


    dictToSend = {}

    match choice:

        case '1':

            print('Query any entry in a table in the database.')
            database = input('Database:')
            table = input('Table:')
            query = input('Query:')

            query = ast.literal_eval(query)

            dictToSend = {'database':database, 'table':table, 'query':query}

            res = rq.post(url + '/database/query', json=dictToSend)
            dictFromServer = res.json()

        case '2':

            print('Update any entry in a table in the database.')

        case '3':

            print('Insert any entry in a table in the database.')
            database = input('Database:')
            table = input('Table:')
            data = input('Data:')
            context = input('Context:')

            data = ast.literal_eval(data)
            context = ast.literal_eval(context)

            dictToSend = {'database':database, 'table':table, 'data':data, 'context':context}

            res = rq.post(url + '/database/insert', json=dictToSend)
            dictFromServer = res.json()

        case '4':

            print('Delete any entry in a table in the database.')
            database = input('Database:')
            table = input('Table:')
            query = input('Query:')

            query = ast.literal_eval(query)

            dictToSend = {'database':database, 'table':table, 'query':query}

            res = rq.post(url + '/database/delete', json=dictToSend)
            dictFromServer = res.json()
        
    return dictFromServer

debug = True
if debug:
    url = 'http://192.168.0.13:5001'
else:
    url = 'https://laserfocus-api.onrender.com'

message = 'Enter a choice or press enter to exit: '
print(
"""
1. Database
2. Drive
3. Wallet
"""
)
choice = input(message)
print('\n')

match choice:
    case '1':
        response = databaseInterface()
    case '2':
        response = driveInterface()
    case '3':
        response = walletInterface()
    case '':
        print('Exiting...')
    case _:
        print('Invalid choice')

print('Response:', response)
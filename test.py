import requests as rq

account = 'Cash'
file_name = '072024.csv'
url = 'http://192.168.0.13:5001'

dictToSend = {'account': account, 'file_name':file_name}
res = rq.post(url + '/wallet/bac/generateStatements', json=dictToSend)
dictFromServer = res.json()

print('API Response:', dictFromServer)

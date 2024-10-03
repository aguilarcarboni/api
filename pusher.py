import requests as rq

res = rq.post('http://127.0.0.1:5002/database/read', json={'table': 'user', 'params':{'name':'Andres'}})
print(res.json())
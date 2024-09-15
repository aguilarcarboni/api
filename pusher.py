import requests as rq

res = rq.post('http://127.0.0.1:5001/database/read', json={'table': 'user', 'query': {'name':'Andres'}})
print(res.json())
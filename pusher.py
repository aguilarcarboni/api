import requests as rq

res = rq.post('http://127.0.0.1:5001/database/create', json={'table': 'space', 'data': {'name':'Test Space', 'status':'active', 'visibility':'private', "user_id": 3}})
print(res.json())
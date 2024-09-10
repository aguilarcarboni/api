import requests as rq

api_url = 'http://127.0.0.1:5001'
endpoint = '/api/pusher'
payload = {'message': 'Hello, World!'}

response = rq.post(api_url + endpoint, json=payload)
print(response.json())
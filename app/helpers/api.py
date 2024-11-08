import requests
import os

url = f"127.0.0.1:{os.getenv('LF_API_PORT')}"

def access_api(endpoint, method='GET', data=None):
    auth = requests.post(url + '/login', json={
        'username': 'admin',
        'password': 'password'
    })
    response = requests.request(method, url + endpoint, json=data, headers={
        'Authorization': f'Bearer {auth.json()["access_token"]}'
    })
    try:
        return response.json()
    except:
        return response.content
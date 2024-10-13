import requests
response = requests.post('http://192.168.0.33:8080/login', json={'token': 'laserfocused'})
token = response.json()['access_token']
print(token)

response = requests.get('http://192.168.0.33:8080/', headers={'Authorization': f'Bearer {token}'})
print(response.json())
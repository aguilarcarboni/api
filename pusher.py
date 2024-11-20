import requests

response = requests.post('http://localhost:5000/login', json={'token': 'laserfocused'})
access_token = response.json()['access_token']

response = requests.get('http://localhost:5000/tv/fetch_playlist', headers={'Authorization': f'Bearer {access_token}'})
print(response.json())
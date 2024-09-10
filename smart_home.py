import requests as rq
import json


response = rq.post("http://127.0.0.1:5001/home/get_states")
content_dict = json.loads(response.json()['content'])
print(content_dict['result'][0])

for entity in content_dict['result']:
    print(entity, '\n')

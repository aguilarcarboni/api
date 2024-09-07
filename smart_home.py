import requests as rq


response = rq.post("http://127.0.0.1:5000/home/light_off", json={"lightId": "light.bedroom_cieling"})
print(response)

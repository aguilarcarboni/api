import requests

url = "https://api.render.com/v1/services/srv-cp70p6vsc6pc73cop0gg/restart"

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_Al1SfIArIVSWrEZBOnXkzielJHuN"
}

response = requests.post(url, headers=headers)

print(response.text)
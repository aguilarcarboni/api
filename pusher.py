from app.helpers.api import access_api

response = access_api('/news/personalized')
print(response, len(response))
import requests

url = "http://xdplayer.tv:8080"
username = "aguilarcarboni"
password = "pXU2Hx6NMu"

request = f"/player_api.php?username={username}&password={password}&action=get_vod_streams"
request2 = f"/player_api.php?username={username}&password={password}&action=get_live_streams"
request3 = f"/get.php?username={username}&password={password}&type=m3u_plus&output=ts"

print('Fetching playlist...')
response = requests.get(url + request3)
print(response.status_code, response.text.splitlines()[0:5])

# Save the first 500 lines of the m3u file
with open('playlist.m3u', 'w', encoding='utf-8') as f:
    lines = response.text.splitlines()
    length = len(lines)
    for i, line in enumerate(lines[:int(1500)]):
        f.write(line + '\n')

print("Saved M3U file as 'playlist.m3u'")
import requests

url = "http://xdplayer.tv:8080"
username = "aguilarcarboni"
password = "pXU2Hx6NMu"

request = f"/player_api.php?username={username}&password={password}&action=get_vod_streams"
request2 = f"/player_api.php?username={username}&password={password}&action=get_live_streams"
request3 = f"/get.php?username={username}&password={password}&type=m3u_plus&output=ts"

print('Fetching playlist...')
response = requests.get(url + request3)
if response.status_code != 200:
    print(f'Failed to fetch playlist: {response.status_code}')
    exit(1)
print('Playlist fetched successfully')

# Save the first 500 lines of the m3u file
print('Saving playlist...')
with open('playlist.m3u', 'w', encoding='utf-8') as f:
    lines = response.text.splitlines()
    for i, line in enumerate(lines[:int(2000)]):
        if i % 100 == 0:
            print(f'Writing {i}/{len(lines)} lines...')
        f.write(line + '\n')

print('Playlist saved successfully')
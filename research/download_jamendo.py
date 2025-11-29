import requests
import os

CLIENT_ID = "fa7dd0ab"  # Jamendo developer client id 넣기
SAVE_DIR = "./jamendo_downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

params = {
    "client_id": CLIENT_ID,
    "format": "json",
    "limit": 200,                    # 최대 200곡
    "audioformat": "mp32",           # mp3 고정 비트레이트
    "license_cc": "by,sa,by-sa,cc0", # 쓸 수 있는 라이선스만 필터링
    "order": "popularity_total"
}

url = "https://api.jamendo.com/v3.0/tracks/"

r = requests.get(url, params=params)
data = r.json()

for track in data['results']:
    audio_url = track['audio']
    name = f"{track['artist_name']} - {track['name']}.mp3".replace("/", "_")
    path = os.path.join(SAVE_DIR, name)

    print("Downloading:", name)
    audio_data = requests.get(audio_url).content
    with open(path, "wb") as f:
        f.write(audio_data)

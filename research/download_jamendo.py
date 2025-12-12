import argparse
import time
import requests
import json
import os
from dotenv import load_dotenv

# 백엔드 디렉토리의 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")

SAVE_DIR = "./jamendo_downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

params = {
    "client_id": CLIENT_ID,
    "format": "json",
    "limit": 200,                    # 최대 200곡
    "audioformat": "mp32",           # mp3 고정 비트레이트
    "license_cc": "by,sa,by-sa,cc0", # 사용 가능한 라이선스만 필터링
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

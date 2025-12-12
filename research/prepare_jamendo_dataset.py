
import os
import requests
import json
import glob
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import argparse
from dotenv import load_dotenv

# 백엔드 디렉토리의 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

# --- 상수 ---
JAMENDO_TO_FMA_MAP = {
    'pop': 'Pop',
    'rock': 'Rock',
    'electronic': 'Electronic',
    'hiphop': 'Hip-Hop',
    'jazz': 'Jazz',
    'folk': 'Folk',
    'classical': 'Classical',
    'instrumental': 'Instrumental',
    'metal': 'Rock', # Map to Rock
    'alternative': 'Rock', # Map to Rock
    'indie': 'Rock', # Map to Rock
    'dance': 'Electronic',
    'techno': 'Electronic',
    'house': 'Electronic',
    'ambient': 'Experimental', 
    'songwriter': 'Folk',
    'soundtrack': 'Instrumental',
    'chillout': 'Electronic'
}

def download_tracks(client_id, save_dir, limit=200):
    print(f"--- Step 1: Downloading Tracks (Limit: {limit}) ---")
    os.makedirs(save_dir, exist_ok=True)
    
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": client_id,
        "format": "json",
        "limit": limit,
        "audioformat": "mp32",
        "license_cc": "by,sa,by-sa,cc0",
        "order": "popularity_total"
    }
    
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"Error fetching API: {e}")
        return

    download_count = 0
    results = data.get('results', [])
    print(f"Found {len(results)} tracks via API.")

    for track in results:
        name = f"{track['artist_name']} - {track['name']}.mp3".replace("/", "_")
        path = os.path.join(save_dir, name)
        
        if os.path.exists(path):
            continue

        try:
            print(f"Downloading: {name}")
            audio_data = requests.get(track['audio']).content
            with open(path, "wb") as f:
                f.write(audio_data)
            download_count += 1
        except Exception as e:
            print(f"Failed to download {name}: {e}")

    print(f"Downloaded {download_count} new tracks.")

def generate_metadata(audio_dir, output_jsonl, genre_map):
    print(f"--- Step 2: Generating Metadata JSONL ---")
    mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
    print(f"Scanning {len(mp3_files)} files in {audio_dir}...")
    
    valid_count = 0
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for file_path in mp3_files:
            try:
                audio = MP3(file_path, ID3=EasyID3)
                tags = audio.get('genre', [])
                
                # Extract primary genre
                jamendo_genre = None
                if tags:
                    # Normalized check
                    for tag in tags:
                        t = tag.lower()
                        if t in genre_map:
                            jamendo_genre = t
                            break
                        # Partial match check? (e.g. pop/rock)
                        for k in genre_map:
                            if k in t:
                                jamendo_genre = k
                                break
                        if jamendo_genre: break
                
                if not jamendo_genre:
                    continue # Skip if no mappable genre found
                    
                fma_genre = genre_map[jamendo_genre]
                
                # Create Metadata Object (Simulating FMA structure)
                # Parse ID/Title from filename or tags if possible
                # Filename format: "Artist - Title.mp3"
                filename = os.path.basename(file_path)
                
                # Assign a pseudo ID based on hash or just random? 
                # Or try to read ID tag if available? Jamendo API returns ID but we might have lost it if we only have files.
                # Let's use hash of filename as ID for consistency
                track_id = abs(hash(filename)) % 10000000 
                
                meta = {
                    "track_id": track_id,
                    "filename": filename,
                    "genre": fma_genre,
                    "original_genre": jamendo_genre,
                    "file_path": file_path,
                    # Placeholders for evaluate_model compatibility
                     "instrumentation": {"source": None},
                     "affect": {"valence": None, "energy": None},
                     "mood_style": None
                }
                
                f.write(json.dumps(meta) + '\n')
                valid_count += 1
                
            except Exception as e:
                # print(f"Error scanning {file_path}: {e}")
                pass
                
    print(f"Generated metadata for {valid_count} tracks at {output_jsonl}")

def main():
    parser = argparse.ArgumentParser(description='Prepare Jamendo Dataset')
    parser.add_argument('--client_id', type=str, default=DEFAULT_CLIENT_ID, help='Jamendo Client ID')
    parser.add_argument('--output_dir', type=str, default='./jamendo_dataset', help='Root directory for dataset')
    parser.add_argument('--limit', type=int, default=200, help='Max tracks to download')
    parser.add_argument('--download_only', action='store_true', help='Skip metadata generation')
    
    args = parser.parse_args()
    
    audio_dir = os.path.join(args.output_dir, 'audio')
    jsonl_path = os.path.join(args.output_dir, 'jamendo_metadata.jsonl')
    
    # 1. 다운로드
    download_tracks(args.client_id, audio_dir, args.limit)
    
    # 2. 메타데이터 생성
    if not args.download_only:
        generate_metadata(audio_dir, jsonl_path, JAMENDO_TO_FMA_MAP)

if __name__ == '__main__':
    main()

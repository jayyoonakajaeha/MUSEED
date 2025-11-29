import os
import glob
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

JAMENDO_DIR = "/home/jay/MusicAI/jamendo_downloads"

def scan_genres():
    mp3_files = glob.glob(os.path.join(JAMENDO_DIR, "*.mp3"))
    genres = set()
    
    print(f"Scanning {len(mp3_files)} files...")
    
    for file_path in mp3_files:
        try:
            audio = MP3(file_path, ID3=EasyID3)
            tags = audio.get('genre')
            if tags:
                for g in tags:
                    genres.add(g)
        except Exception:
            pass
            
    print("\n--- Found Genres ---")
    for g in sorted(list(genres)):
        print(g)

if __name__ == "__main__":
    scan_genres()

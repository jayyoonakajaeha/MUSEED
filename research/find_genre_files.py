import os
import glob
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

JAMENDO_DIR = "/home/jay/MusicAI/jamendo_downloads"
TARGET_GENRE = "singersongwriter" # 찾고자 하는 장르

def find_genre_files():
    mp3_files = glob.glob(os.path.join(JAMENDO_DIR, "*.mp3"))
    found_files = []
    
    print(f"Scanning {len(mp3_files)} files for genre '{TARGET_GENRE}'...")
    
    for file_path in mp3_files:
        try:
            audio = MP3(file_path, ID3=EasyID3)
            tags = audio.get('genre')
            if tags:
                if TARGET_GENRE in [g.lower() for g in tags]:
                    found_files.append(file_path)
        except Exception:
            pass
            
    if found_files:
        print(f"\n--- Files with genre '{TARGET_GENRE}' ---")
        for f in found_files:
            print(f)
    else:
        print(f"\nNo files found with genre '{TARGET_GENRE}'.")

if __name__ == "__main__":
    find_genre_files()
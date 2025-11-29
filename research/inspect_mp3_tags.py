import os
import sys

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3
    print("Mutagen library is available.")
except ImportError:
    print("Mutagen library is NOT available.")
    sys.exit(1)

file_path = "jamendo_downloads/A Virtual Friend - Paris La Nuit.mp3"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

try:
    audio = MP3(file_path, ID3=EasyID3)
    print("--- ID3 Tags ---")
    for key in audio.keys():
        print(f"{key}: {audio[key]}")
    
    if 'genre' in audio:
        print(f"Genre found: {audio['genre']}")
    else:
        print("No genre tag found.")
        
except Exception as e:
    print(f"Error reading tags: {e}")

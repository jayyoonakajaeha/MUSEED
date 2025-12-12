
import os
import sys
import json
import glob
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from sqlalchemy.orm import sessionmaker

# Add the app's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from app import models

# Configuration
JAMENDO_METADATA_PATH = '/home/jay/MusicAI/MUSEED/data/jamendo_rich_metadata.jsonl'
AUDIO_DIR = '/home/jay/MusicAI/jamendo_formatted/data/900'

def import_jamendo_tracks():
    print("--- Starting Jamendo Import Script ---")
    
    if not os.path.exists(JAMENDO_METADATA_PATH):
        print(f"Error: Metadata file {JAMENDO_METADATA_PATH} does not exist.")
        return
    if not os.path.exists(AUDIO_DIR):
        print(f"Error: Audio directory {AUDIO_DIR} does not exist.")
        return

    # 1. Read Rich Metadata
    print(f"Reading metadata from {JAMENDO_METADATA_PATH}...")
    jamendo_enrich_map = {}
    with open(JAMENDO_METADATA_PATH, 'r') as f:
        for line in f:
            data = json.loads(line)
            jamendo_enrich_map[data['track_id']] = data
    
    # 2. Scan files in AUDIO_DIR
    print(f"Scanning audio files in {AUDIO_DIR}...")
    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.mp3"))
    print(f"Found {len(audio_files)} files.")
    
    tracks_to_add = []
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        existing_ids = set(t[0] for t in session.query(models.Track.track_id).all())
        
        for file_path in audio_files:
            try:
                # Filename is like "900000.mp3"
                basename = os.path.basename(file_path)
                track_id_str = os.path.splitext(basename)[0]
                try:
                    track_id = int(track_id_str)
                except ValueError:
                    continue
                
                if track_id in existing_ids:
                    continue
                
                # Resolve symlink to get original filename "Artist - Title.mp3"
                real_path = os.path.realpath(file_path)
                real_basename = os.path.basename(real_path)
                name_part = os.path.splitext(real_basename)[0]
                
                # Attempt to split Artist - Title
                if " - " in name_part:
                    artist_name, title = name_part.split(" - ", 1)
                else:
                    artist_name = "Jamendo Artist"
                    title = name_part
                
                # Get Duration via Mutagen
                try:
                    audio = MP3(real_path)
                    duration = int(audio.info.length)
                except:
                    duration = 0
                
                # Get Genre from Rich Metadata
                genre_toplevel = "Unknown"
                if track_id in jamendo_enrich_map:
                    # Map simplified genre if available
                    rich_data = jamendo_enrich_map[track_id]
                    if 'genre' in rich_data:
                        genre_toplevel = rich_data['genre'].capitalize()
                
                new_track = models.Track(
                    track_id=track_id,
                    title=title,
                    artist_name=artist_name,
                    duration=duration,
                    album_art_url=None, # No album art available locally
                    genre_toplevel=genre_toplevel
                )
                tracks_to_add.append(new_track)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        if tracks_to_add:
            print(f"Adding {len(tracks_to_add)} tracks to database...")
            session.bulk_save_objects(tracks_to_add)
            session.commit()
            print("Import successful!")
        else:
            print("No new tracks to add.")

    except Exception as e:
        print(f"Database Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import_jamendo_tracks()

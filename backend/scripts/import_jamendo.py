import os
import sys
import glob
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import models, database

# Directory containing Jamendo MP3s
JAMENDO_DIR = "/home/jay/MusicAI/jamendo_downloads"
START_TRACK_ID = 200000

# Explicit Mapping (prioritized matches)
# Jamendo genres from scan_genres.py output, mapped to FMA Top 16
GENRE_MAP = {
    "8bit": "Electronic",
    "ambient": "Experimental",
    "country": "Country",
    "dance": "Electronic",
    "electronic": "Electronic",
    "folk": "Folk",
    "funk": "Soul-RnB",
    "house": "Electronic",
    "indie": "Rock", # Indie is broad, but often leans rock/pop. Default to Rock.
    "jazz": "Jazz",
    "pop": "Pop",
    "rock": "Rock",
    "soul": "Soul-RnB",
    "synthpop": "Pop",
    "chillout": "Easy Listening",
    "dreampop": "Pop",
    "dubstep": "Electronic",
    "filmscore": "Instrumental",
    "hiphop": "Hip-Hop",
    "newage": "Easy Listening",
    "rnb": "Soul-RnB",
    "singersongwriter": "Pop", # Changed from Folk to Pop based on user feedback
    
    # FMA Top Genres that might appear in Jamendo tags
    "blues": "Blues",
    "classical": "Classical",
    "experimental": "Experimental",
    "instrumental": "Instrumental",
    "international": "International",
    "spoken": "Spoken",
    "old-time / historic": "Old-Time / Historic"
}

def get_db_session():
    engine = database.engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def map_genre(genre_tags_list):
    if not genre_tags_list:
        return "Experimental" # Default fallback if no genre tags at all
    
    # Prioritize FMA Top-level genres
    fma_top_genres = [
        "International", "Blues", "Jazz", "Classical", "Old-Time / Historic", 
        "Country", "Pop", "Rock", "Easy Listening", "Soul-RnB", 
        "Electronic", "Hip-Hop", "Spoken", "Experimental", "Folk", "Instrumental"
    ]

    # Clean and flatten genre tags from mutagen (e.g., ['Pop, Folk, Indie'])
    processed_tags = []
    for tag_item in genre_tags_list:
        processed_tags.extend([t.strip().lower() for t in tag_item.split(',')])

    # 1. Direct and Specific Keyword Mapping
    for tag in processed_tags:
        if tag in GENRE_MAP:
            return GENRE_MAP[tag]

    # 2. General Keyword Matching (if no direct map found)
    for tag in processed_tags:
        if "rock" in tag: return "Rock"
        if "pop" in tag: return "Pop"
        if "blues" in tag: return "Blues"
        if "jazz" in tag: return "Jazz"
        if "folk" in tag: return "Folk"
        if "country" in tag: return "Country"
        if "electronic" in tag or "synth" in tag or "dance" in tag or "house" in tag or "dubstep" in tag: return "Electronic"
        if "hiphop" in tag or "hip-hop" in tag or "rap" in tag: return "Hip-Hop"
        if "soul" in tag or "rnb" in tag or "funk" in tag: return "Soul-RnB"
        if "instrumental" in tag: return "Instrumental"
        if "classical" in tag: return "Classical"
        if "experimental" in tag or "ambient" in tag: return "Experimental"
        if "spoken" in tag: return "Spoken"
        if "easy listening" in tag or "chillout" in tag or "newage" in tag: return "Easy Listening"
        if "international" in tag: return "International"

    return "Pop" # Default fallback to Pop if nothing else matches

def import_tracks():
    if not os.path.exists(JAMENDO_DIR):
        print(f"Directory not found: {JAMENDO_DIR}")
        return

    db = get_db_session()
    mp3_files = glob.glob(os.path.join(JAMENDO_DIR, "*.mp3"))
    
    print(f"Found {len(mp3_files)} MP3 files.")
    
    current_id = START_TRACK_ID
    count = 0
    
    for file_path in mp3_files:
        try:
            audio = MP3(file_path, ID3=EasyID3)
            
            # Filename fallback for title
            filename = os.path.basename(file_path).replace('.mp3', '')
            fname_artist = "Unknown Artist"
            fname_title = filename
            if " - " in filename:
                parts = filename.split(" - ", 1)
                fname_artist = parts[0]
                fname_title = parts[1]

            title = audio.get('title', [fname_title])[0]
            artist = audio.get('artist', [fname_artist])[0]
            
            mapped_genre = map_genre(audio.get('genre')) # Pass the full list of tags
            duration = int(audio.info.length)
            
            # Check if track already exists (by title/artist to avoid dupes if re-run)
            existing = db.query(models.Track).filter(
                models.Track.title == title,
                models.Track.artist_name == artist
            ).first()
            
            if existing:
                print(f"Skipping existing: {title} - {artist} ({existing.track_id})")
                continue

            new_track = models.Track(
                track_id=current_id,
                title=title,
                artist_name=artist,
                duration=duration,
                genre_toplevel=mapped_genre,
                album_art_url=None 
            )
            
            db.add(new_track)
            print(f"Importing [{current_id}] {title} - {artist} ({mapped_genre})")
            current_id += 1
            count += 1
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    db.commit()
    print(f"Successfully imported {count} tracks starting from ID {START_TRACK_ID}.")
    db.close()

if __name__ == "__main__":
    import_tracks()
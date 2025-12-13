import os
import sys
import pandas as pd
import numpy as np
import ast
from sqlalchemy.orm import sessionmaker

# Add the app's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from app import models

# --- Configuration ---
# Detect environment: Docker (has /app/data) vs Local (Host)

if os.path.exists('/app/data'):
    # Docker Environment
    print("Detected Docker Environment. Using container paths.")
    FMA_DATA_PATH = '/app/data'
    FMA_METADATA_PATH = '/app/data/fma_metadata'
    FMA_EMBEDDINGS_PATH = '/app/data/embeddings'
else:
    # Local Host Environment (Default)
    print("Detected Local Environment. Using host paths.")
    FMA_DATA_PATH = '/home/jay/MusicAI/fma/data'
    FMA_METADATA_PATH = os.path.join(FMA_DATA_PATH, 'fma_metadata')
    FMA_EMBEDDINGS_PATH = '/home/jay/MusicAI/MUSEED/data/embeddings_contrastive_v2_mean'

# Change source to raw_tracks.csv
FMA_TRACKS_CSV_PATH = os.path.join(FMA_METADATA_PATH, 'raw_tracks.csv') 
FMA_GENRES_CSV_PATH = os.path.join(FMA_METADATA_PATH, 'genres.csv')
BATCH_SIZE = 1000

def transform_album_art_url(url: str) -> str:
    """
    Transforms the raw FMA image URL into a usable, resized image URL.
    Returns None if the input URL is invalid.
    """
    if not isinstance(url, str) or not url.startswith('https://freemusicarchive.org/file/'):
        return None
    
    new_url = url.replace('/file/', '/image/?file=')
    return f"{new_url}&width=290&height=290&type=album"

def parse_duration(duration_str: str) -> int:
    """Converts a 'MM:SS' or 'HH:MM:SS' string to total seconds."""
    if not isinstance(duration_str, str):
        return 0
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 2: # MM:SS
        return parts[0] * 60 + parts[1]
    if len(parts) == 3: # HH:MM:SS
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0

def create_genre_map():
    """
    Reads genres.csv and creates a mapping from any genre_id to its top-level genre name.
    """
    print("Creating genre map...")
    try:
        genres_df = pd.read_csv(FMA_GENRES_CSV_PATH)
        id_to_name = pd.Series(genres_df.title.values, index=genres_df.genre_id).to_dict()
        id_to_toplevel_id = pd.Series(genres_df.top_level.values, index=genres_df.genre_id).to_dict()
        genre_map = {
            genre_id: id_to_name.get(toplevel_id)
            for genre_id, toplevel_id in id_to_toplevel_id.items()
        }
        print("Genre map created successfully.")
        return genre_map
    except Exception as e:
        print(f"Error creating genre map: {e}")
        return None

def import_metadata():
    """
    Finds all existing embedding files, looks up their metadata in raw_tracks.csv, 
    enriches genre and album art data, and populates the 'tracks' table.
    """
    print("--- Starting FMA Metadata Import (Embedding-First, raw_tracks.csv) ---")

    genre_map = create_genre_map()
    if genre_map is None:
        return

    # Ensure all tables are created
    print("Creating database tables if they don't exist...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # Create a new session
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = Session()

    try:
        if db_session.query(models.Track).first() is not None:
            print("The 'tracks' table is not empty. Aborting import.")
            return

        print(f"Reading FMA metadata from {FMA_TRACKS_CSV_PATH}...")
        # raw_tracks.csv has a simple header. Use track_id as index.
        tracks_df = pd.read_csv(FMA_TRACKS_CSV_PATH, index_col='track_id')
        
        print(f"Scanning for embedding files in {FMA_EMBEDDINGS_PATH}...")
        embedding_files = [f for f in os.listdir(FMA_EMBEDDINGS_PATH) if f.endswith('.npy')]
        print(f"Found {len(embedding_files)} embedding files.")

        tracks_to_add = []
        total_added_count = 0
        
        for filename in embedding_files:
            try:
                track_id = int(os.path.splitext(filename)[0])
            except ValueError:
                continue

            try:
                row = tracks_df.loc[track_id]
            except KeyError:
                continue

            # Assuming column names from raw_tracks.csv
            title = row.get('track_title')
            artist_name = row.get('artist_name')
            duration_str = row.get('track_duration')
            
            if pd.isna(title) or pd.isna(artist_name) or pd.isna(duration_str):
                continue

            duration = parse_duration(duration_str)

            # Transform album art URL
            raw_art_url = row.get('track_image_file')
            album_art_url = transform_album_art_url(raw_art_url)

            # Get top-level genre, or infer it if missing
            genre_toplevel = row.get('track_genre_top')
            if pd.isna(genre_toplevel):
                try:
                    # Assuming 'track_genres' column contains a list of genre dicts
                    genres_list = ast.literal_eval(row.get('track_genres', '[]'))
                    if genres_list and isinstance(genres_list, list) and len(genres_list) > 0:
                        first_genre_id = genres_list[0]['genre_id']
                        inferred_genre = genre_map.get(int(first_genre_id))
                        genre_toplevel = inferred_genre
                except (ValueError, SyntaxError):
                    genre_toplevel = None
            
            new_track = models.Track(
                track_id=track_id,
                title=str(title),
                artist_name=str(artist_name),
                duration=duration,
                album_art_url=album_art_url,
                genre_toplevel=str(genre_toplevel) if pd.notna(genre_toplevel) else None
            )
            tracks_to_add.append(new_track)

            if len(tracks_to_add) >= BATCH_SIZE:
                db_session.bulk_save_objects(tracks_to_add)
                db_session.commit()
                total_added_count += len(tracks_to_add)
                print(f"Added batch of {len(tracks_to_add)}. Total added so far: {total_added_count}")
                tracks_to_add = []

        if tracks_to_add:
            db_session.bulk_save_objects(tracks_to_add)
            db_session.commit()
            total_added_count += len(tracks_to_add)

        print(f"\nTotal tracks successfully imported: {total_added_count}")
        print("\n--- FMA Metadata Import Complete! ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == '__main__':
    import_metadata()

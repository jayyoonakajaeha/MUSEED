
import os
import sys
from sqlalchemy.orm import sessionmaker

# Add the app's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from app import models

def fix_positions():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        playlists = session.query(models.Playlist).all()
        print(f"Found {len(playlists)} playlists to check.")

        fixed_count = 0
        for playlist in playlists:
            # Check if all positions are 0 (or duplicates exist)
            tracks = session.query(models.PlaylistTrack).filter(
                models.PlaylistTrack.playlist_id == playlist.id
            ).order_by(models.PlaylistTrack.id).all() # Order by ID to preserve insertion order

            needs_fix = False
            seen_positions = set()
            for t in tracks:
                if t.position in seen_positions:
                    needs_fix = True
                    break
                seen_positions.add(t.position)
            
            # Also check if all are 0
            if len(tracks) > 1 and all(t.position == 0 for t in tracks):
                needs_fix = True

            if needs_fix:
                print(f"Fixing playlist '{playlist.name}' (ID: {playlist.id})...")
                for index, track in enumerate(tracks):
                    track.position = index
                fixed_count += 1
        
        session.commit()
        print(f"Successfully fixed positions for {fixed_count} playlists.")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_positions()

import os
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas, models
from ..dependencies import get_db

router = APIRouter(
    prefix="/api/tracks",
    tags=["tracks"],
)

FMA_FULL_PATH = "/home/jay/MusicAI/fma/data/fma_full"
JAMENDO_DIR = "/home/jay/MusicAI/jamendo_downloads"

def get_track_path(track_id: int, db: Session) -> Optional[str]:
    """
    Constructs the full path to an audio file.
    Handles both FMA tracks (ID < 200000) and Jamendo tracks (ID >= 200000).
    """
    if track_id < 200000:
        # FMA Track logic
        track_id_str = f"{track_id:06d}"
        folder = track_id_str[:3]
        path = os.path.join(FMA_FULL_PATH, folder, f"{track_id_str}.mp3")
        if os.path.exists(path):
            return path
    else:
        # Jamendo Track logic
        # Need to query DB to get filename (Artist - Title.mp3)
        track = crud.search_tracks(db, query=str(track_id), limit=1) # Search by ID
        if track:
            track = track[0]
            # Try exact filename match
            filename = f"{track.artist_name} - {track.title}.mp3"
            path = os.path.join(JAMENDO_DIR, filename)
            if os.path.exists(path):
                return path
            
            # Fallback: Try finding file that contains title if artist match fails or naming is different
            # This is a bit expensive but Jamendo filenames can be tricky
            import glob
            # Escape glob characters if necessary, but for now try simple search
            candidates = glob.glob(os.path.join(JAMENDO_DIR, f"*{track.title}*.mp3"))
            if candidates:
                return candidates[0]

    return None

@router.get("/search", response_model=List[schemas.Track])
def search_for_tracks(
    q: Optional[str] = Query(None, min_length=2),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    if q is None:
        return []
    db_tracks = crud.search_tracks(db, query=q, skip=skip, limit=limit)
    
    response_tracks = []
    for track in db_tracks:
        # Check if the audio file exists before adding it to the list
        if get_track_path(track.track_id, db):
            track_schema = schemas.Track.from_orm(track)
            track_schema.audio_url = f"/api/tracks/{track.track_id}/stream"
            response_tracks.append(track_schema)
            
    return response_tracks

@router.get("/{track_id}/stream")
def stream_track(track_id: int, db: Session = Depends(get_db)):
    track_path = get_track_path(track_id, db)
    
    print("--- STREAMING DEBUG ---")
    print(f"[DEBUG] Streaming request for track_id: {track_id}")
    print(f"[DEBUG] Constructed file path: {track_path}")
    file_exists = track_path and os.path.exists(track_path)
    print(f"[DEBUG] Does file exist? {file_exists}")
    print("-----------------------")

    if not track_path or not file_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    return FileResponse(track_path, media_type="audio/mpeg")

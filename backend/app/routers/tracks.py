import os
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/api/tracks",
    tags=["tracks"],
)

FMA_FULL_PATH = "/home/jay/MusicAI/fma/data/fma_full"

def get_track_path(track_id: int) -> Optional[str]:
    """
    Constructs the full path to an FMA track file if it exists.
    Example: track_id 2 -> /path/to/fma_full/000/000002.mp3
    """
    track_id_str = f"{track_id:06d}"
    folder = track_id_str[:3]
    path = os.path.join(FMA_FULL_PATH, folder, f"{track_id_str}.mp3")
    if os.path.exists(path):
        return path
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
        if get_track_path(track.track_id):
            track_schema = schemas.Track.from_orm(track)
            track_schema.audio_url = f"/api/tracks/{track.track_id}/stream"
            response_tracks.append(track_schema)
            
    return response_tracks

@router.get("/{track_id}/stream")
def stream_track(track_id: int):
    track_path = get_track_path(track_id)
    
    print("--- STREAMING DEBUG ---")
    print(f"[DEBUG] Streaming request for track_id: {track_id}")
    print(f"[DEBUG] Constructed file path: {track_path}")
    file_exists = os.path.exists(track_path)
    print(f"[DEBUG] Does file exist? {file_exists}")
    print("-----------------------")

    if not track_path or not file_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    return FileResponse(track_path, media_type="audio/mpeg")

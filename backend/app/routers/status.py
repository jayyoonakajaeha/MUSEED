from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, models
from ..dependencies import get_db

router = APIRouter(
    prefix="/api",
    tags=["status"]
)

@router.get("/status")
def get_status():
    """
    백엔드 실행 상태 확인 엔드포인트
    """
    return {"status": "ok"}

@router.get("/stats")
def get_global_stats(db: Session = Depends(get_db)):
    track_count = db.query(models.Track).count()
    user_count = db.query(models.User).count()
    playlist_count = db.query(models.Playlist).count()
    
    return {
        "tracks": track_count,
        "users": user_count,
        "playlists": playlist_count
    }

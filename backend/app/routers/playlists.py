
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user, get_current_user_optional
from ..tasks import generate_playlist_task, generate_playlist_from_id_task

# --- Router Setup ---
router = APIRouter(
    prefix="/api/playlists",
    tags=["playlists"]
)

# --- Constants ---
TEMP_UPLOAD_DIR = "/tmp/museed_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)


# --- API Endpoints ---

@router.get("/discover", response_model=List[schemas.Playlist])
def get_discover_playlists(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    탐색(Discover)용 공개 플레이리스트 목록 조회
    """
    playlists = crud.get_public_playlists(db, skip=skip, limit=limit)
    for playlist in playlists:
        if current_user:
            playlist.liked_by_user = current_user in playlist.liked_by
        else:
            playlist.liked_by_user = False
    return playlists

@router.get("/trending", response_model=List[schemas.Playlist])
def get_trending_playlists(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    트렌딩 플레이리스트 조회
    """
    playlists = crud.get_trending_playlists(db, limit=limit)
    for playlist in playlists:
        if current_user:
            playlist.liked_by_user = current_user in playlist.liked_by
        else:
            playlist.liked_by_user = False
    return playlists

@router.get("/search", response_model=List[schemas.Playlist])
def search_for_playlists(
    q: Optional[str] = Query(None, min_length=2),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    플레이리스트 검색
    """
    if q is None:
        return []
    playlists = crud.search_playlists(db, query=q, skip=skip, limit=limit)
    for playlist in playlists:
        if current_user:
            playlist.liked_by_user = current_user in playlist.liked_by
        else:
            playlist.liked_by_user = False
    return playlists

@router.post("/upload", response_model=schemas.TaskSubmission, status_code=status.HTTP_202_ACCEPTED)
async def create_ai_playlist_from_upload(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    [비동기] 오디오 파일 업로드 기반 AI 플레이리스트 생성 시작
    Returns: 태스크 ID
    """
    # 1. 임시 파일 저장
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(TEMP_UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload file: {e}")
    
    # 2. Celery 태스크 요청
    owner_id = current_user.id if current_user else None
    task = generate_playlist_task.delay(name=name, file_path=file_path, owner_id=owner_id)
    
    return schemas.TaskSubmission(task_id=task.id)


@router.post("", response_model=schemas.TaskSubmission, status_code=status.HTTP_202_ACCEPTED)
def create_ai_playlist_from_id(
    playlist_in: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    [비동기] ID 기반 플레이리스트 생성 작업 시작
    Returns: 태스크 ID
    """
    owner_id = current_user.id if current_user else None
    task = generate_playlist_from_id_task.delay(
        name=playlist_in.name, 
        seed_track_id=playlist_in.seed_track_id, 
        owner_id=owner_id
    )
    
    return schemas.TaskSubmission(task_id=task.id)

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    """
    Celery 작업 상태 조회
    """
    from ..worker import celery_app
    task_result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return response

@router.get("/{playlist_id}", response_model=schemas.Playlist)
def read_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user_optional)):
    """
    플레이리스트 상세 정보 조회
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if current_user:
        db_playlist.liked_by_user = current_user in db_playlist.liked_by
    else:
        db_playlist.liked_by_user = False
    
    return db_playlist

@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    플레이리스트 삭제
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this playlist")
    
    crud.delete_playlist(db, playlist_id=playlist_id)
    return {"message": "Playlist deleted successfully"}

@router.post("/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_201_CREATED)
def add_track_to_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    플레이리스트에 곡 추가
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")
    
    success = crud.add_track_to_playlist(db, playlist_id=playlist_id, track_id=track_id)
    if not success:
         raise HTTPException(status_code=400, detail="Failed to add track (track might not exist)")
    
    return {"message": "Track added to playlist"}

@router.delete("/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track_from_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    플레이리스트에서 곡 삭제
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")
        
    success = crud.remove_track_from_playlist(db, playlist_id=playlist_id, track_id=track_id)
    if not success:
        raise HTTPException(status_code=404, detail="Track not found in playlist")
    
    return {"message": "Track removed from playlist"}

@router.delete("/{playlist_id}/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist_entry(
    playlist_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    플레이리스트 엔트리 삭제
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")
        
    success = crud.remove_playlist_entry(db, playlist_id=playlist_id, entry_id=entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist entry not found")
    
    return {"message": "Playlist entry removed successfully"}

@router.put("/{playlist_id}/tracks/reorder", status_code=status.HTTP_200_OK)
def reorder_playlist_tracks(
    playlist_id: int,
    reorder_request: schemas.BaseModel, # Using base model as wrapper if explicit class not available here, but verify imports
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Need to redefine ReorderTracksRequest here or import?
    # It was defined inline previously.
    # Let's import logic or define it.
    pass 
    # Wait, I am overwriting the file. I should copy the existing CRUD logic properly.
    # ReorderTracksRequest was defined in previous file. I'll re-add it.

class ReorderTracksRequest(schemas.BaseModel):
    track_ids: List[int]

@router.put("/{playlist_id}/tracks/reorder", status_code=status.HTTP_200_OK)
def reorder_playlist_tracks(
    playlist_id: int,
    reorder_request: ReorderTracksRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")
        
    crud.reorder_playlist_tracks(db, playlist_id=playlist_id, track_ids=reorder_request.track_ids)
    return {"message": "Tracks reordered successfully"}


@router.put("/{playlist_id}", response_model=schemas.Playlist)
def update_playlist(
    playlist_id: int,
    playlist_update: schemas.PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    플레이리스트 수정
    """
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this playlist")
    
    updated_playlist = crud.update_playlist(db, playlist_id=playlist_id, playlist_update=playlist_update)
    if updated_playlist is None:
        raise HTTPException(status_code=500, detail="Failed to update playlist")
    
    updated_playlist.liked_by_user = current_user in updated_playlist.liked_by
    return updated_playlist

@router.post("/{playlist_id}/like", response_model=schemas.Playlist)
def like_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.like_playlist(db, playlist_id=playlist_id, user_id=current_user.id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db_playlist.liked_by_user = True
    return db_playlist

@router.delete("/{playlist_id}/like", response_model=schemas.Playlist)
def unlike_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.unlike_playlist(db, playlist_id=playlist_id, user_id=current_user.id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db_playlist.liked_by_user = False
    return db_playlist

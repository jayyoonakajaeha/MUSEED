from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.get("/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    # This is a public endpoint, no auth required for now
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/{username}/stats", response_model=schemas.UserStats)
def read_user_stats(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    top_genre_result = crud.get_top_genre_for_user(db, user_id=db_user.id)
    
    top_genre = top_genre_result.genre if top_genre_result else None
    
    return schemas.UserStats(top_genre=top_genre)

@router.put("/{username}", response_model=schemas.User)
def update_user_profile(
    username: str,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Authorization: Ensure the user is updating their own profile
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this profile.",
        )
    
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the new username is already taken
    if user_in.username and user_in.username != db_user.username:
        existing_user = crud.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken.")

    # Check if the new email is already taken
    if user_in.email and user_in.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    return crud.update_user(db=db, db_user=db_user, user_in=user_in)

@router.get("/{username}/playlists", response_model=List[schemas.Playlist])
def get_user_created_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    playlists = crud.get_user_playlists(db, user_id=db_user.id)
    for playlist in playlists:
        playlist.liked_by_user = current_user in playlist.liked_by
    return playlists

@router.get("/{username}/likes", response_model=List[schemas.Playlist])
def get_user_liked_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    liked_playlists = crud.get_liked_playlists(db, user_id=db_user.id)
    for playlist in liked_playlists:
        playlist.liked_by_user = current_user in playlist.liked_by
    return liked_playlists

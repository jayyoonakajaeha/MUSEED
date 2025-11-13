from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import func
from . import models, schemas, security
from typing import List

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    # Eagerly load playlists and their tracks to prevent N+1 query issues
    return db.query(models.User).options(
        subqueryload(models.User.playlists).options(
            subqueryload(models.Playlist.tracks).options(
                joinedload(models.PlaylistTrack.track)
            )
        )
    ).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate):
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
    
    if "email" in update_data and update_data["email"]:
        db_user.email = update_data["email"]

    if "username" in update_data and update_data["username"]:
        db_user.username = update_data["username"]

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Listening History CRUD ---

def create_listening_history(db: Session, history: schemas.ListeningHistoryCreate, user_id: int):
    db_history = models.ListeningHistory(
        track_id=int(history.track_id), 
        genre=history.genre, 
        user_id=user_id
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_top_genre_for_user(db: Session, user_id: int):
    top_genre_query = (
        db.query(
            models.ListeningHistory.genre,
            func.count(models.ListeningHistory.id).label("listen_count"),
        )
        .filter(models.ListeningHistory.user_id == user_id)
        .group_by(models.ListeningHistory.genre)
        .order_by(func.count(models.ListeningHistory.id).desc())
        .first()
    )
    return top_genre_query

# --- Playlist CRUD ---

def get_playlist(db: Session, playlist_id: int):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track)
    ).filter(models.Playlist.id == playlist_id).first()

def create_playlist(db: Session, name: str, owner_id: int, track_ids: List[int]):
    # Create the playlist entry
    db_playlist = models.Playlist(name=name, owner_id=owner_id, is_public=True) # Assuming public by default
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)

    # Create the track entries
    for track_id in track_ids:
        db_track = models.PlaylistTrack(playlist_id=db_playlist.id, track_id=track_id)
        db.add(db_track)
    
    db.commit()
    db.refresh(db_playlist)
    # Re-fetch the playlist with all relationships loaded for the response
    return get_playlist(db, db_playlist.id)


# --- Track CRUD ---

def search_tracks(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_query = f"%{query}%"
    from sqlalchemy import or_
    return db.query(models.Track).filter(
        or_(
            models.Track.title.ilike(search_query),
            models.Track.artist_name.ilike(search_query)
        )
    ).offset(skip).limit(limit).all()

# --- Auth ---

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user
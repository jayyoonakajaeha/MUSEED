from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import func, desc, or_
from . import models, schemas, security
from typing import List, Optional
from datetime import datetime, timedelta, timezone

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    # Eagerly load relationships for profile page
    return db.query(models.User).options(
        subqueryload(models.User.playlists).options(
            joinedload(models.Playlist.owner), # Eager load the owner of each playlist
            subqueryload(models.Playlist.tracks).options(
                joinedload(models.PlaylistTrack.track)
            ),
            subqueryload(models.Playlist.liked_by)
        ),
        subqueryload(models.User.liked_playlists).options(
            joinedload(models.Playlist.owner), # Eager load the owner of each liked playlist
            subqueryload(models.Playlist.tracks).options(
                joinedload(models.PlaylistTrack.track)
            ),
            subqueryload(models.Playlist.liked_by)
        ),
        joinedload(models.User.followers),
        joinedload(models.User.following)
    ).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def search_users(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_query = f"%{query}%"
    # Search by username (ID) or nickname
    return db.query(models.User).filter(
        or_(
            models.User.username.ilike(search_query),
            models.User.nickname.ilike(search_query)
        )
    ).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    # Create user with username (ID) and nickname
    db_user = models.User(
        username=user.username, 
        nickname=user.nickname,
        email=user.email, # Optional
        hashed_password=hashed_password
    )
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

    if "nickname" in update_data and update_data["nickname"]:
        db_user.nickname = update_data["nickname"]

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def follow_user(db: Session, follower: models.User, followed: models.User):
    if follower.id == followed.id:
        return None # Users cannot follow themselves
    if followed not in follower.following:
        follower.following.append(followed)
        db.commit()
    return follower

def unfollow_user(db: Session, follower: models.User, followed: models.User):
    if followed in follower.following:
        follower.following.remove(followed)
        db.commit()
    return follower

def get_user_followers(db: Session, username: str):
    user = db.query(models.User).options(joinedload(models.User.followers)).filter(models.User.username == username).first()
    return user.followers if user else []

def get_user_following(db: Session, username: str):
    user = db.query(models.User).options(joinedload(models.User.following)).filter(models.User.username == username).first()
    return user.following if user else []

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

def get_genre_distribution_for_user(db: Session, user_id: int):
    return (
        db.query(
            models.ListeningHistory.genre,
            func.count(models.ListeningHistory.id).label("count"),
        )
        .filter(models.ListeningHistory.user_id == user_id)
        .group_by(models.ListeningHistory.genre)
        .order_by(func.count(models.ListeningHistory.id).desc())
        .all()
    )

# --- Playlist CRUD ---

def get_playlist(db: Session, playlist_id: int):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by) # Eager load who liked this playlist
    ).filter(models.Playlist.id == playlist_id).first()

def get_public_playlists(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by)
    ).filter(models.Playlist.is_public == True).order_by(desc(models.Playlist.created_at)).offset(skip).limit(limit).all()

def get_trending_playlists(db: Session, limit: int = 10):
    """
    Fetches playlists with the most likes in the last 24 hours.
    Falls back to recent public playlists if not enough trending data.
    """
    threshold = datetime.now(timezone.utc) - timedelta(hours=24)

    # Subquery to count likes per playlist in the last 24h
    stmt = (
        db.query(
            models.playlist_likes.c.playlist_id,
            func.count('*').label('like_count')
        )
        .filter(models.playlist_likes.c.liked_at >= threshold)
        .group_by(models.playlist_likes.c.playlist_id)
        .order_by(desc('like_count'))
        .limit(limit)
        .subquery()
    )

    # Join with Playlist model to get full objects
    trending_playlists = (
        db.query(models.Playlist)
        .join(stmt, models.Playlist.id == stmt.c.playlist_id)
        .options(
            joinedload(models.Playlist.owner),
            subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
            subqueryload(models.Playlist.liked_by)
        )
        .filter(models.Playlist.is_public == True) 
        .order_by(stmt.c.like_count.desc())
        .all()
    )

    # If we don't have enough trending playlists, fill with recent public ones
    if len(trending_playlists) < limit:
        needed = limit - len(trending_playlists)
        existing_ids = [p.id for p in trending_playlists]
        
        fallback_playlists = (
            db.query(models.Playlist)
            .options(
                joinedload(models.Playlist.owner),
                subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
                subqueryload(models.Playlist.liked_by)
            )
            .filter(
                models.Playlist.is_public == True,
                models.Playlist.id.notin_(existing_ids)
            )
            .order_by(desc(models.Playlist.created_at))
            .limit(needed)
            .all()
        )
        trending_playlists.extend(fallback_playlists)

    return trending_playlists

def search_playlists(db: Session, query: str, skip: int = 0, limit: int = 10):
    search_query = f"%{query}%"
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by)
    ).filter(
        models.Playlist.is_public == True,
        models.Playlist.name.ilike(search_query)
    ).order_by(desc(models.Playlist.created_at)).offset(skip).limit(limit).all()

def get_user_playlists(db: Session, user_id: int):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by)
    ).filter(models.Playlist.owner_id == user_id).all()

def get_liked_playlists(db: Session, user_id: int):
    user = db.query(models.User).options(
        subqueryload(models.User.liked_playlists).options(
            joinedload(models.Playlist.owner),
            subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
            subqueryload(models.Playlist.liked_by)
        )
    ).filter(models.User.id == user_id).first()
    return user.liked_playlists if user else []

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

def update_playlist(db: Session, playlist_id: int, playlist_update: schemas.PlaylistUpdate):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if not db_playlist:
        return None
    
    update_data = playlist_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_playlist, key, value)
    
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return get_playlist(db, db_playlist.id)

def delete_playlist(db: Session, playlist_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if db_playlist:
        db.delete(db_playlist)
        db.commit()
        return True
    return False

def like_playlist(db: Session, playlist_id: int, user_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_playlist or not db_user:
        return None

    # Check if already liked
    if db_user not in db_playlist.liked_by:
        db_playlist.liked_by.append(db_user)
        db.commit()
        db.refresh(db_playlist)
    return get_playlist(db, db_playlist.id)

def unlike_playlist(db: Session, playlist_id: int, user_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_playlist or not db_user:
        return None

    # Check if liked
    if db_user in db_playlist.liked_by:
        db_playlist.liked_by.remove(db_user)
        db.commit()
        db.refresh(db_playlist)
    return get_playlist(db, db_playlist.id)

# --- Track CRUD ---

def search_tracks(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_query = f"%{query}%"
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
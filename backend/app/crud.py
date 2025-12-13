from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import func, desc, or_
from sqlalchemy.exc import IntegrityError
from . import models, schemas, security
from typing import List, Optional
from datetime import datetime, timedelta, timezone

# --- 활동 CRUD ---

def create_activity(
    db: Session, 
    user_id: int, 
    action_type: str, 
    target_playlist_id: Optional[int] = None, 
    target_user_id: Optional[int] = None
):
    db_activity = models.Activity(
        user_id=user_id,
        action_type=action_type,
        target_playlist_id=target_playlist_id,
        target_user_id=target_user_id
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_feed_activities(db: Session, user_id: int, limit: int = 20):
    """
    사용자가 팔로우한 사람들의 활동 조회 (메소드 설명 제외)
    """
    # 팔로우한 ID 목록 조회
    user = db.query(models.User).options(joinedload(models.User.following)).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    following_ids = [u.id for u in user.following]
    
    if not following_ids:
        return []

    return db.query(models.Activity).options(
        joinedload(models.Activity.user),
        joinedload(models.Activity.target_playlist).joinedload(models.Playlist.owner),
        joinedload(models.Activity.target_playlist).subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track), # 커버 아트를 위한 트랙 로드
        joinedload(models.Activity.target_user)
    ).filter(
        models.Activity.user_id.in_(following_ids)
    ).order_by(desc(models.Activity.created_at)).limit(limit).all()


# --- 사용자 CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).options(
        subqueryload(models.User.playlists).options(
            joinedload(models.Playlist.owner),
            subqueryload(models.Playlist.tracks).options(
                joinedload(models.PlaylistTrack.track)
            ),
            subqueryload(models.Playlist.liked_by)
        ),
        subqueryload(models.User.liked_playlists).options(
            joinedload(models.Playlist.owner),
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
    return db.query(models.User).filter(
        or_(
            models.User.username.ilike(search_query),
            models.User.nickname.ilike(search_query)
        )
    ).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        nickname=user.nickname,
        email=user.email, 
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
        return None
    if followed not in follower.following:
        follower.following.append(followed)
        db.commit()
        # 활동 기록
        create_activity(db, follower.id, models.ActivityType.FOLLOW_USER, target_user_id=followed.id)
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

# --- 청취 기록 CRUD ---

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

# --- 플레이리스트 CRUD ---

def get_playlist(db: Session, playlist_id: int):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by)
    ).filter(models.Playlist.id == playlist_id).first()

def get_public_playlists(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.owner),
        subqueryload(models.Playlist.tracks).joinedload(models.PlaylistTrack.track),
        subqueryload(models.Playlist.liked_by)
    ).filter(models.Playlist.is_public == True).order_by(desc(models.Playlist.created_at)).offset(skip).limit(limit).all()

def get_trending_playlists(db: Session, limit: int = 10):
    threshold = datetime.now(timezone.utc) - timedelta(hours=24)
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
    db_playlist = models.Playlist(name=name, owner_id=owner_id, is_public=True)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)

    for index, track_id in enumerate(track_ids):
        db_track = models.PlaylistTrack(playlist_id=db_playlist.id, track_id=track_id, position=index)
        db.add(db_track)
    
    db.commit()
    db.refresh(db_playlist)
    
    # 로그인 사용자의 경우만 활동 기록
    if owner_id is not None:
        create_activity(db, owner_id, models.ActivityType.CREATE_PLAYLIST, target_playlist_id=db_playlist.id)
    
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

def add_track_to_playlist(db: Session, playlist_id: int, track_id: int):
    # 트랙 존재 확인
    track = db.query(models.Track).filter(models.Track.track_id == track_id).first()
    if not track:
        return False

    # 새로운 위치 계산 (마지막 + 1)
    last_position = db.query(func.max(models.PlaylistTrack.position)).filter(models.PlaylistTrack.playlist_id == playlist_id).scalar()
    new_position = (last_position if last_position is not None else -1) + 1

    db_track = models.PlaylistTrack(playlist_id=playlist_id, track_id=track_id, position=new_position)
    db.add(db_track)
    db.commit()
    return True

def remove_playlist_entry(db: Session, playlist_id: int, entry_id: int):
    db_entry = db.query(models.PlaylistTrack).filter(
        models.PlaylistTrack.playlist_id == playlist_id,
        models.PlaylistTrack.id == entry_id
    ).first()
    
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False

def remove_track_from_playlist(db: Session, playlist_id: int, track_id: int):
    db_track_association = db.query(models.PlaylistTrack).filter(
        models.PlaylistTrack.playlist_id == playlist_id,
        models.PlaylistTrack.track_id == track_id
    ).first()
    
    if db_track_association:
        db.delete(db_track_association)
        db.commit()
        return True
    return False

def reorder_playlist_tracks(db: Session, playlist_id: int, track_ids: List[int]):
    # 쿼리 최소화를 위해 모든 연관 관계 조회
    tracks = db.query(models.PlaylistTrack).filter(
        models.PlaylistTrack.playlist_id == playlist_id,
        models.PlaylistTrack.track_id.in_(track_ids)
    ).all()
    
    # 빠른 조회를 위한 맵 생성
    track_map = {t.track_id: t for t in tracks}
    
    for index, track_id in enumerate(track_ids):
        if track_id in track_map:
            track_map[track_id].position = index
            
    db.commit()
    return True

def delete_playlist(db: Session, playlist_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if db_playlist:
        # Fix: Manually delete related Activities to prevent FK violation
        db.query(models.Activity).filter(models.Activity.target_playlist_id == playlist_id).delete(synchronize_session=False)
        
        db.delete(db_playlist)
        db.commit()
        return True
    return False

def like_playlist(db: Session, playlist_id: int, user_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_playlist or not db_user:
        return None

    # 이미 좋아요 했는지 확인
    if db_user not in db_playlist.liked_by:
        try:
            db_playlist.liked_by.append(db_user)
            db.commit()
            db.refresh(db_playlist)
            # 활동 기록
            create_activity(db, user_id, models.ActivityType.LIKE_PLAYLIST, target_playlist_id=playlist_id)
        except IntegrityError:
            db.rollback()
            # 경쟁 조건으로 이미 좋아요 된 경우
            pass
        
    return get_playlist(db, db_playlist.id)

def unlike_playlist(db: Session, playlist_id: int, user_id: int):
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_playlist or not db_user:
        return None

    # 좋아요 했는지 확인
    if db_user in db_playlist.liked_by:
        db_playlist.liked_by.remove(db_user)
        db.commit()
        db.refresh(db_playlist)
    return get_playlist(db, db_playlist.id)

# --- 트랙 CRUD ---

def search_tracks(db: Session, query: str, skip: int = 0, limit: int = 100):
    if query.isdigit():
        return db.query(models.Track).filter(models.Track.track_id == int(query)).all()
        
    search_query = f"%{query}%"
    return db.query(models.Track).filter(
        or_(
            models.Track.title.ilike(search_query),
            models.Track.artist_name.ilike(search_query)
        )
    ).offset(skip).limit(limit).all()

# --- 인증 ---

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user
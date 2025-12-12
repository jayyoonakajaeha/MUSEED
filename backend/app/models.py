from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

# --- 연관 테이블 정의 (Association Tables) ---

# 사용자가 좋아요한 플레이리스트 저장 (N:M 관계)
playlist_likes = Table(
    'playlist_likes', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('liked_at', DateTime(timezone=True), server_default=func.now())
)

# 사용자 팔로우/팔로잉 관계 저장 (N:M, 자기 참조)
followers_assoc = Table(
    'followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# --- 열거형 정의 (Enums) ---

class ActivityType(str, enum.Enum):
    """사용자 활동 피드용 활동 유형 정의"""
    CREATE_PLAYLIST = "created a new playlist"
    LIKE_PLAYLIST = "liked"
    FOLLOW_USER = "started following"

# --- 데이터 모델 정의 (Models) ---

class User(Base):
    """사용자 정보 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) # 로그인 ID
    nickname = Column(String, index=True, nullable=False) # 표시 이름
    email = Column(String, unique=True, index=True, nullable=True) # 이메일 (선택)
    hashed_password = Column(String, nullable=False) # 암호화된 비밀번호
    is_active = Column(Boolean, default=True) # 계정 활성 상태
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 정의
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    listening_history = relationship("ListeningHistory", back_populates="user")
    
    # 다대다 관계: 좋아요한 플레이리스트
    liked_playlists = relationship("Playlist", secondary=playlist_likes, back_populates="liked_by")

    # 다대다 관계: 팔로잉 (내가 팔로우하는)
    following = relationship(
        'User', 
        secondary=followers_assoc,
        primaryjoin=(followers_assoc.c.follower_id == id),
        secondaryjoin=(followers_assoc.c.followed_id == id),
        back_populates='followers'
    )
    # 다대다 관계: 팔로워 (나를 팔로우하는)
    followers = relationship(
        'User', 
        secondary=followers_assoc,
        primaryjoin=(followers_assoc.c.followed_id == id),
        secondaryjoin=(followers_assoc.c.follower_id == id),
        back_populates='following'
    )
    
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan", foreign_keys="[Activity.user_id]")


class Playlist(Base):
    """플레이리스트 모델"""
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # 플레이리스트 제목
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # 생성자 ID (게스트 허용)
    is_public = Column(Boolean, default=True) # 공개 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 정의
    owner = relationship("User", back_populates="playlists")
    # tracks: 재생 순서 포함한 곡 목록
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistTrack.position")
    
    # 다대다 관계: 좋아요한 사용자
    liked_by = relationship("User", secondary=playlist_likes, back_populates="liked_playlists")


class PlaylistTrack(Base):
    """플레이리스트-트랙 매핑 테이블 (재생 순서 포함)"""
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), nullable=False)
    position = Column(Integer, default=0) # 재생 순서 (0부터)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlist_associations")


class Track(Base):
    """음원 정보 모델 (FMA 기반)"""
    __tablename__ = "tracks"

    track_id = Column(Integer, primary_key=True, index=True) # FMA 원본 ID
    title = Column(String, index=True) # 제목
    artist_name = Column(String, index=True) # 아티스트
    duration = Column(Integer) # 재생 시간 (초)
    album_art_url = Column(String, nullable=True) # 커버 이미지 URL
    genre_toplevel = Column(String, nullable=True) # 상위 장르

    playlist_associations = relationship("PlaylistTrack", back_populates="track")
    listening_history = relationship("ListeningHistory", back_populates="track")


class ListeningHistory(Base):
    """청취 기록 모델"""
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), nullable=False)
    genre = Column(String, nullable=True) # 청취 당시 장르 (통계용)
    listened_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="listening_history")
    track = relationship("Track", back_populates="listening_history")

class Activity(Base):
    """사용자 활동 피드 모델"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 활동 주체
    action_type = Column(String, nullable=False) # 활동 유형
    
    # 활동 대상 (플레이리스트 또는 사용자)
    target_playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activities", foreign_keys=[user_id])
    target_playlist = relationship("Playlist")
    target_user = relationship("User", foreign_keys=[target_user_id])

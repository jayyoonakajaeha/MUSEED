from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

# Association table for Playlist likes
playlist_likes = Table(
    'playlist_likes', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('liked_at', DateTime(timezone=True), server_default=func.now())
)

# Association table for User follows
followers_assoc = Table(
    'followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class ActivityType(str, enum.Enum):
    CREATE_PLAYLIST = "created a new playlist"
    LIKE_PLAYLIST = "liked"
    FOLLOW_USER = "started following"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) # User ID
    nickname = Column(String, index=True, nullable=False) # Display Name
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    listening_history = relationship("ListeningHistory", back_populates="user")
    
    liked_playlists = relationship("Playlist", secondary=playlist_likes, back_populates="liked_by")

    following = relationship(
        'User', 
        secondary=followers_assoc,
        primaryjoin=(followers_assoc.c.follower_id == id),
        secondaryjoin=(followers_assoc.c.followed_id == id),
        back_populates='followers'
    )
    followers = relationship(
        'User', 
        secondary=followers_assoc,
        primaryjoin=(followers_assoc.c.followed_id == id),
        secondaryjoin=(followers_assoc.c.follower_id == id),
        back_populates='following'
    )
    
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan", foreign_keys="[Activity.user_id]")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistTrack.position")
    
    liked_by = relationship("User", secondary=playlist_likes, back_populates="liked_playlists")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), nullable=False)
    position = Column(Integer, default=0) # Added position for ordering
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlist_associations")


class Track(Base):
    __tablename__ = "tracks"

    track_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist_name = Column(String, index=True)
    duration = Column(Integer)
    album_art_url = Column(String, nullable=True)
    genre_toplevel = Column(String, nullable=True)

    playlist_associations = relationship("PlaylistTrack", back_populates="track")
    listening_history = relationship("ListeningHistory", back_populates="track")


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), nullable=False)
    genre = Column(String, nullable=True)
    listened_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="listening_history")
    track = relationship("Track", back_populates="listening_history")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False) # CREATE_PLAYLIST, LIKE_PLAYLIST, FOLLOW_USER
    
    # Target ID (Playlist ID or User ID depending on action)
    # We store ID only to keep it simple, or we can use separate nullable FKs.
    # Using nullable FKs is safer for referential integrity.
    target_playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activities", foreign_keys=[user_id])
    target_playlist = relationship("Playlist")
    target_user = relationship("User", foreign_keys=[target_user_id])
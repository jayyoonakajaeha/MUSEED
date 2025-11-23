from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) # This is the User ID
    nickname = Column(String, index=True, nullable=False) # This is the Display Name
    email = Column(String, unique=True, index=True, nullable=True) # Made nullable
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


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")
    
    liked_by = relationship("User", secondary=playlist_likes, back_populates="liked_playlists")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.track_id"), nullable=False)
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

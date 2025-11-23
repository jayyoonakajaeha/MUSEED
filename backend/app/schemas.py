from pydantic import BaseModel, EmailStr, field_validator, Field, computed_field
from typing import Optional, List, Any
from datetime import datetime
from . import models

# --- Track Schemas ---
class TrackBase(BaseModel):
    track_id: int
    title: str
    artist_name: str
    duration: int
    album_art_url: Optional[str] = None
    genre_toplevel: Optional[str] = None

class Track(TrackBase):
    audio_url: Optional[str] = None

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# --- Listening History Schemas ---
class ListeningHistoryBase(BaseModel):
    track_id: int
    genre: str

class ListeningHistoryCreate(ListeningHistoryBase):
    pass

class ListeningHistory(ListeningHistoryBase):
    id: int
    user_id: int
    listened_at: datetime

    class Config:
        from_attributes = True

# --- Playlist Track Schemas ---
class PlaylistTrackBase(BaseModel):
    track_id: int

class PlaylistTrackCreate(PlaylistTrackBase):
    pass

class PlaylistTrack(PlaylistTrackBase):
    id: int
    playlist_id: int

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    nickname: str
    email: Optional[str] = None # Changed from EmailStr to str, and made default None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None # ID usually shouldn't change, but keeping it optional
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserStats(BaseModel):
    top_genre: Optional[str] = None

# Schema for genre distribution
class GenreStat(BaseModel):
    genre: str
    count: int

# Schema for simplified user lists (followers/following)
class UserForList(BaseModel):
    id: int
    username: str
    nickname: str # Added nickname
    profile_image_key: str

# Schema for User Recommendation
class UserRecommendation(UserForList):
    similarity: float

# Schema for the owner field within a Playlist
class PlaylistOwner(BaseModel):
    id: int
    username: str
    nickname: str # Added nickname

    class Config:
        from_attributes = True

# --- Playlist Schemas ---
class PlaylistBase(BaseModel):
    name: str
    is_public: bool = True

class PlaylistCreate(BaseModel):
    name: str
    seed_track_id: int

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None

class Playlist(PlaylistBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: PlaylistOwner
    tracks: List[Track] = []
    liked_by: List[PlaylistOwner] = []
    liked_by_user: bool = False # This will be set dynamically in the router

    @computed_field
    @property
    def likes_count(self) -> int:
        return len(self.liked_by)

    @field_validator('tracks', mode='before')
    @classmethod
    def extract_tracks_from_playlist_tracks(cls, v):
        if v and isinstance(v, list) and len(v) > 0 and isinstance(v[0], models.PlaylistTrack):
            # Extract the actual Track objects
            tracks = [pt.track for pt in v if pt.track is not None]
            # Manually add the audio_url to each track
            for track in tracks:
                track.audio_url = f"/api/tracks/{track.track_id}/stream"
            return tracks
        return v

    class Config:
        from_attributes = True

class UserForProfile(UserBase):
    id: int
    is_active: bool
    listening_history: List[ListeningHistory] = []

    class Config:
        from_attributes = True

# This full User schema depends on Playlist, so it must come after.
class User(UserBase):
    id: int
    is_active: bool
    playlists: List[Playlist] = []
    liked_playlists: List[Playlist] = []
    
    # Fields for follow feature
    is_followed_by_current_user: bool = False # Set dynamically
    
    # Relationship fields needed for computation
    followers: List[Any] = Field(default=[], exclude=True) 
    following: List[Any] = Field(default=[], exclude=True)

    @computed_field
    @property
    def followers_count(self) -> int:
        return len(self.followers)

    @computed_field
    @property
    def following_count(self) -> int:
        return len(self.following)

    class Config:
        from_attributes = True

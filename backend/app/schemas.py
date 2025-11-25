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

# --- Achievement Schema ---
class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str 

# --- Playlist Owner Schema ---
class PlaylistOwner(BaseModel):
    id: int
    username: str
    nickname: str

    class Config:
        from_attributes = True

# --- Playlist Track Response Schema ---
class PlaylistTrackResponse(BaseModel):
    id: int
    position: int
    track: Track

    class Config:
        from_attributes = True

# --- User For List Schema (Moved Up) ---
class UserForList(BaseModel):
    id: int
    username: str
    nickname: str
    profile_image_key: str

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
    owner_id: Optional[int] = None
    created_at: datetime
    owner: Optional[PlaylistOwner] = None
    tracks: List[PlaylistTrackResponse] = []
    liked_by: List[PlaylistOwner] = []
    liked_by_user: bool = False

    @computed_field
    @property
    def likes_count(self) -> int:
        return len(self.liked_by)

    @field_validator('tracks', mode='before')
    @classmethod
    def process_playlist_tracks(cls, v):
        if v and isinstance(v, list) and len(v) > 0 and isinstance(v[0], models.PlaylistTrack):
            # We need to return the PlaylistTrack objects, but first inject audio_url into the nested track
            for pt in v:
                if pt.track:
                    pt.track.audio_url = f"/api/tracks/{pt.track.track_id}/stream"
            return v
        return v

    class Config:
        from_attributes = True

# --- Activity Schema ---
class Activity(BaseModel):
    id: int
    user: UserForList # Changed from PlaylistOwner to UserForList to include profile_image_key
    action_type: str
    target_playlist: Optional[Playlist] = None
    target_user: Optional[UserForList] = None # Changed to UserForList
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    nickname: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserStats(BaseModel):
    top_genre: Optional[str] = None

class GenreStat(BaseModel):
    genre: str
    count: int

class UserRecommendation(UserForList):
    similarity: float

class UserForProfile(UserBase):
    id: int
    is_active: bool
    listening_history: List[ListeningHistory] = []

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    playlists: List[Playlist] = []
    liked_playlists: List[Playlist] = []
    achievements: List[Achievement] = [] 
    
    is_followed_by_current_user: bool = False
    
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

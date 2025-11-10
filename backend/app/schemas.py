from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# --- Listening History Schemas ---
class ListeningHistoryBase(BaseModel):
    track_id: str
    genre: str

class ListeningHistoryCreate(ListeningHistoryBase):
    pass

class ListeningHistory(ListeningHistoryBase):
    id: int
    user_id: int
    listened_at: datetime

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserStats(BaseModel):
    top_genre: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    listening_history: list[ListeningHistory] = []

    class Config:
        from_attributes = True

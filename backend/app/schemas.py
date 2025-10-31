from pydantic import BaseModel, field_validator


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if not (8 <= len(v) <= 72):
            raise ValueError("Password must be between 8 and 72 characters")
        return v


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import crud, schemas, database, security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(f"--- DEBUG: get_current_user received token: {token[:30]}...") # Print start of token
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        print(f"--- DEBUG: Token decoded successfully. Payload: {payload}") # Print payload
        username: str = payload.get("sub")
        if username is None:
            print("--- DEBUG: Username (sub) is missing from payload.")
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError as e:
        print(f"--- DEBUG: JWTError during token decoding: {e}") # Print JWTError
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        print(f"--- DEBUG: User '{token_data.username}' not found in database.")
        raise credentials_exception
    
    print(f"--- DEBUG: User '{user.username}' authenticated successfully.")
    return user

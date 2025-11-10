from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas, security

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
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

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Listening History CRUD ---

def create_listening_history(db: Session, history: schemas.ListeningHistoryCreate, user_id: int):
    db_history = models.ListeningHistory(**history.model_dump(), user_id=user_id)
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

# --- Auth ---

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas, security
from ..dependencies import get_db

# 인증 관련 API 라우터 정의
router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트
    
    - **username**: 사용자 ID (고유)
    - **nickname**: 표시 이름
    - **password**: 비밀번호
    
    ID 중복 확인 후 새 사용자 생성
    (이메일은 현재 선택사항이므로 제외)
    """
    # 1. 사용자 ID 중복 체크
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="User ID already taken")
    
    # 2. 사용자 생성 및 반환
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    로그인 및 JWT 토큰 발급 엔드포인트
    
    - **username**: 사용자 ID
    - **password**: 비밀번호
    
    인증 성공 시 액세스 토큰 반환
    """
    # 1. 사용자 인증 (ID/PW 확인)
    user = crud.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 액세스 토큰 만료 시간 설정
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. JWT 토큰 생성
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 4. 토큰 반환
    return {"access_token": access_token, "token_type": "bearer"}
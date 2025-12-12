from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user, get_current_user_optional
from ..ml import recommendation

# 사용자 관련 API 라우터
router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

def _get_profile_image_key(db: Session, db_user: models.User) -> str:
    """
    사용자의 활동(주로 듣는 장르, 플레이리스트 생성 여부)에 따라 프로필 이미지 키를 결정
    """
    # 1. 사용자가 가장 많이 들은 장르 확인
    top_genre_result = crud.get_top_genre_for_user(db, user_id=db_user.id)
    if top_genre_result and top_genre_result.genre:
        known_genres = [
            "Blues", "Classical", "Country", "Electronic", "Experimental", 
            "Folk", "Hip-Hop", "Instrumental", "International", "Jazz", 
            "Old-Time / Historic", "Pop", "Rock", "Soul-RnB", "Spoken", 
            "Easy Listening"
        ]
        # 주요 장르에 해당하면 해당 장르 이미지 사용
        if top_genre_result.genre in known_genres:
            # 파일명 불일치 예외 처리
            # "Old-Time / Historic" -> "Old_Time_Historic" (Robust check)
            if "Old-Time" in top_genre_result.genre and "Historic" in top_genre_result.genre:
                return "Old_Time_Historic"
            
            if top_genre_result.genre == "Easy Listening":
                return "Easy_Listening"
            
            return top_genre_result.genre
    
    # 2. 장르 데이터가 없으면 플레이리스트 생성 여부 확인
    playlist_count = db.query(models.Playlist).filter(models.Playlist.owner_id == db_user.id).count()
    if playlist_count > 0:
        return "Default_Headphone" # 헤드폰 쓴 기본 이미지
        
    # 3. 기본 이미지
    return "Default"

def _calculate_achievements(db_user: models.User) -> List[schemas.Achievement]:
    """
    사용자의 활동 통계를 바탕으로 달성한 업적(뱃지) 목록을 계산
    """
    achievements = []
    
    # 1. Seed Planter: 첫 플레이리스트 생성
    playlist_count = len(db_user.playlists)
    if playlist_count >= 1:
        achievements.append(schemas.Achievement(
            id="seed_planter",
            name="Seed Planter",
            description="Created your first playlist.",
            icon="🌱"
        ))
    
    # 2. Curator: 5개 이상 플레이리스트 생성
    if playlist_count >= 5:
        achievements.append(schemas.Achievement(
            id="curator",
            name="Curator",
            description="Created 5 or more playlists.",
            icon="🎨"
        ))

    # 3. Social Butterfly: 5명 이상 팔로우
    following_count = len(db_user.following)
    if following_count >= 5:
        achievements.append(schemas.Achievement(
            id="social_butterfly",
            name="Social Butterfly",
            description="Following 5 or more users.",
            icon="🦋"
        ))

    # 4. Trendsetter: 10명 이상의 팔로워 보유
    followers_count = len(db_user.followers)
    if followers_count >= 10:
        achievements.append(schemas.Achievement(
            id="trendsetter",
            name="Trendsetter",
            description="Has 10 or more followers.",
            icon="🔥"
        ))

    # 5. Music Lover: 10개 이상의 플레이리스트 좋아요
    liked_count = len(db_user.liked_playlists)
    if liked_count >= 10:
        achievements.append(schemas.Achievement(
            id="music_lover",
            name="Music Lover",
            description="Liked 10 or more playlists.",
            icon="❤️"
        ))

    return achievements

def _populate_user_response(db: Session, db_user: models.User, current_user: Optional[models.User]) -> schemas.User:
    """
    DB 모델 객체(User)를 API 응답 스키마(schemas.User)로 변환하고, 부가 정보(팔로우 여부, 좋아요 여부 등)를 채웁니다.
    """
    is_followed = False
    if current_user and db_user.id != current_user.id:
        is_followed = any(follower.id == current_user.id for follower in db_user.followers)

    # Pydantic 모델로 변환
    created_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.playlists]
    liked_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.liked_playlists]
    
    # 현재 로그인한 사용자의 좋아요 여부 체크
    if current_user:
        current_user_liked_playlist_ids = {pl.id for pl in liked_playlists} # 최적화용 Set

        for pl in created_playlists:
            pl.liked_by_user = pl.id in current_user_liked_playlist_ids
        for pl in liked_playlists:
            pl.liked_by_user = True 

    # 업적 계산
    achievements = _calculate_achievements(db_user)

    # 프로필 이미지 키 계산 (전달받은 db 세션 사용)
    profile_image_key = _get_profile_image_key(db, db_user)

    user_response = schemas.User(
        id=db_user.id,
        username=db_user.username,
        nickname=db_user.nickname, 
        email=db_user.email,
        is_active=db_user.is_active,
        playlists=created_playlists,
        liked_playlists=liked_playlists,
        followers=db_user.followers,
        following=db_user.following,
        achievements=achievements,
        profile_image_key=profile_image_key, # Added
        is_followed_by_current_user=is_followed
    )
    return user_response


@router.get("/search", response_model=List[schemas.UserForList])
def search_for_users(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    사용자 검색 엔드포인트 (ID 또는 닉네임)
    """
    try:
        if q is None:
            return []
        users_db = crud.search_users(db, query=q, skip=skip, limit=limit)
        
        users_list = []
        for user in users_db:
            users_list.append(schemas.UserForList(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                profile_image_key=_get_profile_image_key(db, user)
            ))
            
        return users_list
    except Exception as e:
        print(f"Error in search_for_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations", response_model=List[schemas.UserRecommendation])
def get_user_recommendations(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    사용자 추천 엔드포인트 (청취 기록 유사도 기반)
    """
    try:
        similar_users_data = recommendation.get_similar_users(db, current_user.id, limit=limit)
        
        recommendations = []
        for item in similar_users_data:
            user = item["user"]
            similarity = item["similarity"]
            
            recommendations.append(schemas.UserRecommendation(
                id=user.id,
                username=user.username,
                nickname=user.nickname, 
                profile_image_key=_get_profile_image_key(db, user),
                similarity=similarity
            ))
            
        return recommendations
    except Exception as e:
        print(f"Error in get_user_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed", response_model=List[schemas.Activity])
def get_user_feed(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    활동 피드 조회 엔드포인트 (팔로우한 사용자의 활동 내역)
    """
    try:
        activities_db = crud.get_feed_activities(db, current_user.id, limit=limit)
        
        activities_response = []
        for activity in activities_db:
            # 활동 주체 정보
            user_data = schemas.UserForList(
                id=activity.user.id,
                username=activity.user.username,
                nickname=activity.user.nickname,
                profile_image_key=_get_profile_image_key(db, activity.user)
            )
            
            # 활동 대상 (사용자) 정보 (있는 경우)
            target_user_data = None
            if activity.target_user:
                target_user_data = schemas.UserForList(
                    id=activity.target_user.id,
                    username=activity.target_user.username,
                    nickname=activity.target_user.nickname,
                    profile_image_key=_get_profile_image_key(db, activity.target_user)
                )
                
            # 활동 대상 (플레이리스트) 정보 (있는 경우)
            target_playlist_data = None
            if activity.target_playlist:
                target_playlist_data = schemas.Playlist.model_validate(activity.target_playlist)

            activities_response.append(schemas.Activity(
                id=activity.id,
                user=user_data,
                action_type=activity.action_type,
                target_playlist=target_playlist_data,
                target_user=target_user_data,
                created_at=activity.created_at
            ))
            
        return activities_response
    except Exception as e:
        print(f"Error in get_user_feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}", response_model=schemas.User)
def read_user(
    username: str, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    특정 사용자 프로필 정보 조회
    """
    try:
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return _populate_user_response(db, db_user, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{username}/follow", response_model=schemas.User)
def follow_user_endpoint(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    사용자 팔로우
    """
    try:
        user_to_follow = crud.get_user_by_username(db, username=username)
        if not user_to_follow:
            raise HTTPException(status_code=404, detail="User to follow not found")
        
        if current_user.id == user_to_follow.id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")

        crud.follow_user(db, follower=current_user, followed=user_to_follow)
        
        updated_user = crud.get_user_by_username(db, username=username)
        return _populate_user_response(db, updated_user, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in follow_user_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{username}/follow", response_model=schemas.User)
def unfollow_user_endpoint(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    사용자 언팔로우
    """
    try:
        user_to_unfollow = crud.get_user_by_username(db, username=username)
        if not user_to_unfollow:
            raise HTTPException(status_code=404, detail="User to unfollow not found")

        crud.unfollow_user(db, follower=current_user, followed=user_to_unfollow)

        updated_user = crud.get_user_by_username(db, username=username)
        return _populate_user_response(db, updated_user, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in unfollow_user_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/followers", response_model=List[schemas.UserForList])
def get_followers(username: str, db: Session = Depends(get_db)):
    """
    팔로워 목록 조회
    """
    try:
        followers_db = crud.get_user_followers(db, username=username)
        followers_list = [
            schemas.UserForList(
                id=f.id,
                username=f.username,
                nickname=f.nickname, 
                profile_image_key=_get_profile_image_key(db, f)
            ) for f in followers_db
        ]
        return followers_list
    except Exception as e:
        print(f"Error in get_followers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}/following", response_model=List[schemas.UserForList])
def get_following(username: str, db: Session = Depends(get_db)):
    """
    팔로잉 목록 조회
    """
    try:
        following_db = crud.get_user_following(db, username=username)
        following_list = [
            schemas.UserForList(
                id=f.id,
                username=f.username,
                nickname=f.nickname, 
                profile_image_key=_get_profile_image_key(db, f)
            ) for f in following_db
        ]
        return following_list
    except Exception as e:
        print(f"Error in get_following: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/stats", response_model=schemas.UserStats)
def read_user_stats(username: str, db: Session = Depends(get_db)):
    """
    사용자 통계 조회 (현재는 Top Genre만 반환)
    """
    try:
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        top_genre_result = crud.get_top_genre_for_user(db, user_id=db_user.id)
        top_genre = top_genre_result.genre if top_genre_result else None
        return schemas.UserStats(top_genre=top_genre)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_user_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}/genre-stats", response_model=List[schemas.GenreStat])
def get_user_genre_stats(username: str, db: Session = Depends(get_db)):
    """
    사용자 장르별 청취 분포 조회 (차트용 데이터)
    """
    try:
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        genre_stats = crud.get_genre_distribution_for_user(db, user_id=db_user.id)
        return genre_stats
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_genre_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{username}", response_model=schemas.User)
def update_user_profile(
    username: str,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    사용자 프로필 수정 (본인만 가능)
    이메일 중복 체크 로직 제거 (이메일 선택사항)
    """
    try:
        if current_user.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this profile.",
            )
        
        db_user = crud.get_user_by_username(db, username=username)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # ID 변경 시 중복 체크
        if user_in.username and user_in.username != db_user.username:
            existing_user = crud.get_user_by_username(db, username=user_in.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="User ID already taken.")

        updated_db_user = crud.update_user(db=db, db_user=db_user, user_in=user_in)
        reloaded_user = crud.get_user_by_username(db, username=updated_db_user.username)
        return _populate_user_response(db, reloaded_user, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_user_profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}/playlists", response_model=List[schemas.Playlist])
def get_user_created_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    사용자가 생성한 플레이리스트 목록 조회
    """
    try:
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.playlists]
        
        # 본인이 아니면 비공개 플레이리스트는 제외
        if not current_user or current_user.id != db_user.id:
            playlists = [p for p in playlists if p.is_public]

        # 좋아요 여부 체크
        if current_user:
            current_user_full = crud.get_user_by_username(db, username=current_user.username)
            liked_playlist_ids = {pl.id for pl in current_user_full.liked_playlists}
            for playlist in playlists:
                playlist.liked_by_user = playlist.id in liked_playlist_ids
        else:
            for playlist in playlists:
                playlist.liked_by_user = False
            
        return playlists
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_created_playlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}/likes", response_model=List[schemas.Playlist])
def get_user_liked_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """
    사용자가 좋아요한 플레이리스트 목록 조회
    """
    try:
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        liked_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.liked_playlists]
        
        # 보는 사람이 좋아요 했는지 여부 (본인 목록을 볼 때도 필요)
        if current_user:
            current_user_full = crud.get_user_by_username(db, username=current_user.username)
            viewer_liked_ids = {pl.id for pl in current_user_full.liked_playlists}
            for playlist in liked_playlists:
                playlist.liked_by_user = playlist.id in viewer_liked_ids
        else:
            for playlist in liked_playlists:
                playlist.liked_by_user = False
            
        return liked_playlists
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_liked_playlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

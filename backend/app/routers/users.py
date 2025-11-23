from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user, get_current_user_optional
from ..ml import recommendation

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

def _get_profile_image_key(db: Session, db_user: models.User) -> str:
    """Determine the profile image key based on user activity."""
    top_genre_result = crud.get_top_genre_for_user(db, user_id=db_user.id)
    if top_genre_result and top_genre_result.genre:
        known_genres = [
            "Blues", "Classical", "Country", "Electronic", "Experimental", 
            "Folk", "Hip-Hop", "Instrumental", "International", "Jazz", 
            "Old-Time / Historic", "Pop", "Rock", "Soul-RnB", "Spoken", 
            "Easy Listening"
        ]
        if top_genre_result.genre in known_genres:
            return top_genre_result.genre
    
    playlist_count = db.query(models.Playlist).filter(models.Playlist.owner_id == db_user.id).count()
    if playlist_count > 0:
        return "Default_Headphone"
        
    return "Default"

def _calculate_achievements(db_user: models.User) -> List[schemas.Achievement]:
    achievements = []
    
    # 1. Seed Planter: Created first playlist
    playlist_count = len(db_user.playlists)
    if playlist_count >= 1:
        achievements.append(schemas.Achievement(
            id="seed_planter",
            name="Seed Planter",
            description="Created your first playlist.",
            icon="🌱"
        ))
    
    # 2. Curator: Created 5+ playlists
    if playlist_count >= 5:
        achievements.append(schemas.Achievement(
            id="curator",
            name="Curator",
            description="Created 5 or more playlists.",
            icon="🎨"
        ))

    # 3. Social Butterfly: Following 5+ users
    following_count = len(db_user.following)
    if following_count >= 5:
        achievements.append(schemas.Achievement(
            id="social_butterfly",
            name="Social Butterfly",
            description="Following 5 or more users.",
            icon="🦋"
        ))

    # 4. Trendsetter: Has 10+ followers
    followers_count = len(db_user.followers)
    if followers_count >= 10:
        achievements.append(schemas.Achievement(
            id="trendsetter",
            name="Trendsetter",
            description="Has 10 or more followers.",
            icon="🔥"
        ))

    # 5. Music Lover: Liked 10+ playlists
    liked_count = len(db_user.liked_playlists)
    if liked_count >= 10:
        achievements.append(schemas.Achievement(
            id="music_lover",
            name="Music Lover",
            description="Liked 10 or more playlists.",
            icon="❤️"
        ))

    return achievements

def _populate_user_response(db_user: models.User, current_user: Optional[models.User]) -> schemas.User:
    """Helper function to populate the full User schema from an ORM object."""
    is_followed = False
    if current_user and db_user.id != current_user.id:
        is_followed = any(follower.id == current_user.id for follower in db_user.followers)

    # Manually construct playlist responses to ensure correct serialization
    # using model_validate which is the Pydantic v2 equivalent of from_orm
    created_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.playlists]
    liked_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.liked_playlists]
    
    # Set liked_by_user status for each playlist
    if current_user:
        # Create a set of liked playlist IDs for efficient lookup
        current_user_liked_playlist_ids = {pl.id for pl in liked_playlists}

        for pl in created_playlists:
            pl.liked_by_user = pl.id in current_user_liked_playlist_ids
        for pl in liked_playlists:
            pl.liked_by_user = True # All playlists in this list are liked by the current user

    # Calculate Achievements
    achievements = _calculate_achievements(db_user)

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
        achievements=achievements, # Added achievements
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
    Search for users by username.
    """
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

@router.get("/recommendations", response_model=List[schemas.UserRecommendation])
def get_user_recommendations(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get recommended users based on listening history similarity.
    """
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

@router.get("/feed", response_model=List[schemas.Activity])
def get_user_feed(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get activity feed from followed users.
    """
    activities_db = crud.get_feed_activities(db, current_user.id, limit=limit)
    
    activities_response = []
    for activity in activities_db:
        # Manually construct UserForList for user and target_user to include profile_image_key
        user_data = schemas.UserForList(
            id=activity.user.id,
            username=activity.user.username,
            nickname=activity.user.nickname,
            profile_image_key=_get_profile_image_key(db, activity.user)
        )
        
        target_user_data = None
        if activity.target_user:
            target_user_data = schemas.UserForList(
                id=activity.target_user.id,
                username=activity.target_user.username,
                nickname=activity.target_user.nickname,
                profile_image_key=_get_profile_image_key(db, activity.target_user)
            )
            
        # For playlist, we need to convert it to schema to handle tracks validation logic if any,
        # but mainly it's fine as is via from_attributes=True if tracks are loaded.
        # The crud.get_feed_activities joined loaded playlist.owner, but not tracks.
        # We might need tracks for cover image (first track album art). 
        # The Activity schema for playlist doesn't enforce tracks presence unless accessed.
        # Front-end needs cover image.
        
        target_playlist_data = None
        if activity.target_playlist:
            # We need to ensure tracks are loaded if we want to use them for cover image
            # Since crud didn't load them, we might trigger lazy load here or it might be empty.
            # Let's assume basic info is enough and frontend handles missing cover.
            # Or better, update CRUD to load tracks for playlist activities.
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

@router.get("/{username}", response_model=schemas.User)
def read_user(
    username: str, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return _populate_user_response(db_user, current_user)

@router.post("/{username}/follow", response_model=schemas.User)
def follow_user_endpoint(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_to_follow = crud.get_user_by_username(db, username=username)
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User to follow not found")
    
    if current_user.id == user_to_follow.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    crud.follow_user(db, follower=current_user, followed=user_to_follow)
    
    updated_user = crud.get_user_by_username(db, username=username)
    return _populate_user_response(updated_user, current_user)

@router.delete("/{username}/follow", response_model=schemas.User)
def unfollow_user_endpoint(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_to_unfollow = crud.get_user_by_username(db, username=username)
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User to unfollow not found")

    crud.unfollow_user(db, follower=current_user, followed=user_to_unfollow)

    updated_user = crud.get_user_by_username(db, username=username)
    return _populate_user_response(updated_user, current_user)


@router.get("/{username}/followers", response_model=List[schemas.UserForList])
def get_followers(username: str, db: Session = Depends(get_db)):
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

@router.get("/{username}/following", response_model=List[schemas.UserForList])
def get_following(username: str, db: Session = Depends(get_db)):
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


@router.get("/{username}/stats", response_model=schemas.UserStats)
def read_user_stats(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    top_genre_result = crud.get_top_genre_for_user(db, user_id=db_user.id)
    top_genre = top_genre_result.genre if top_genre_result else None
    return schemas.UserStats(top_genre=top_genre)

@router.get("/{username}/genre-stats", response_model=List[schemas.GenreStat])
def get_user_genre_stats(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    genre_stats = crud.get_genre_distribution_for_user(db, user_id=db_user.id)
    return genre_stats

@router.put("/{username}", response_model=schemas.User)
def update_user_profile(
    username: str,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this profile.",
        )
    
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.username and user_in.username != db_user.username:
        existing_user = crud.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="User ID already taken.")

    if user_in.email and user_in.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    updated_db_user = crud.update_user(db=db, db_user=db_user, user_in=user_in)
    reloaded_user = crud.get_user_by_username(db, username=updated_db_user.username)
    return _populate_user_response(reloaded_user, current_user)

@router.get("/{username}/playlists", response_model=List[schemas.Playlist])
def get_user_created_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.playlists]
    
    # We need the full current user's liked playlists to check against
    current_user_full = crud.get_user_by_username(db, username=current_user.username)
    liked_playlist_ids = {pl.id for pl in current_user_full.liked_playlists}

    for playlist in playlists:
        playlist.liked_by_user = playlist.id in liked_playlist_ids
        
    return playlists

@router.get("/{username}/likes", response_model=List[schemas.Playlist])
def get_user_liked_playlists(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    liked_playlists = [schemas.Playlist.model_validate(pl) for pl in db_user.liked_playlists]
    for playlist in liked_playlists:
        playlist.liked_by_user = True # By definition, the user likes all these playlists
        
    return liked_playlists

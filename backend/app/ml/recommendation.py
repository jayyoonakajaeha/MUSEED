import os
import numpy as np
from sqlalchemy.orm import Session
from app import models
from typing import List, Dict, Tuple

# Path to the directory containing .npy embedding files
EMBEDDINGS_DIR = "/home/jay/MusicAI/fma_audio_embeddings"

def get_track_embedding(track_id: int) -> np.ndarray:
    """
    Loads the embedding vector for a given track_id from the .npy file.
    Returns None if the file does not exist.
    """
    file_path = os.path.join(EMBEDDINGS_DIR, f"{track_id}.npy")
    if not os.path.exists(file_path):
        return None
    try:
        # Load and ensure it's a 1D array (flatten if necessary)
        embedding = np.load(file_path)
        return embedding.flatten()
    except Exception as e:
        print(f"Error loading embedding for track {track_id}: {e}")
        return None

def calculate_user_vector(db: Session, user_id: int) -> np.ndarray:
    """
    Calculates the user vector by averaging the embeddings of tracks 
    in the user's listening history.
    """
    history = db.query(models.ListeningHistory).filter(
        models.ListeningHistory.user_id == user_id
    ).all()

    if not history:
        return None

    embeddings = []
    for record in history:
        # Assuming track_id is stored as an integer in ListeningHistory
        emb = get_track_embedding(record.track_id)
        if emb is not None:
            embeddings.append(emb)

    if not embeddings:
        return None

    # Calculate the mean vector
    user_vector = np.mean(embeddings, axis=0)
    return user_vector

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors."""
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return np.dot(v1, v2) / (norm_v1 * norm_v2)

def get_similar_users(db: Session, current_user_id: int, limit: int = 5) -> List[Dict]:
    """
    Finds users with similar listening history based on embedding vectors.
    Returns a list of dicts with 'user' object and 'similarity' score.
    """
    # 1. Calculate current user's vector
    current_user_vector = calculate_user_vector(db, current_user_id)
    
    if current_user_vector is None:
        return []

    # Get current user to find who they are following
    current_user = db.query(models.User).filter(models.User.id == current_user_id).first()
    following_ids = [u.id for u in current_user.following] if current_user else []

    # 2. Get all other users (excluding self AND following)
    other_users = db.query(models.User).filter(
        models.User.id != current_user_id,
        models.User.id.notin_(following_ids)
    ).all()
    
    similarities = []

    for user in other_users:
        # 3. Calculate other user's vector
        # Optimization: In a real app, these should be cached or pre-computed
        other_user_vector = calculate_user_vector(db, user.id)
        
        if other_user_vector is not None:
            score = cosine_similarity(current_user_vector, other_user_vector)
            if score > 0: # Filter out non-similar or zero vectors
                similarities.append({
                    "user": user,
                    "similarity": float(score)
                })

    # 4. Sort by similarity (descending)
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    
    return similarities[:limit]

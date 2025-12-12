import os
import numpy as np
from sqlalchemy.orm import Session
from app import models
from typing import List, Dict, Tuple

# Path to the directory containing .npy embedding files
EMBEDDINGS_DIR = "/home/jay/MusicAI/MUSEED/data/embeddings/"
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

from sklearn.cluster import KMeans

def calculate_user_vector(db: Session, user_id: int, n_clusters: int = 3) -> np.ndarray:
    """
    Calculates user 'vectors' using K-Means clustering on listening history.
    Returns: (K, D) array of centroids.
    If history < K, returns mean or available points.
    """
    history = db.query(models.ListeningHistory).filter(
        models.ListeningHistory.user_id == user_id
    ).all()

    if not history:
        return None

    embeddings = []
    for record in history:
        emb = get_track_embedding(record.track_id)
        if emb is not None:
            embeddings.append(emb)

    if not embeddings:
        return None
    
    embeddings_np = np.array(embeddings)
    
    # If not enough data for clustering, return simple mean (reshaped to 1xDim)
    if len(embeddings) < n_clusters:
        return np.mean(embeddings_np, axis=0).reshape(1, -1)
    
    # K-Means Clustering
    try:
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        kmeans.fit(embeddings_np)
        return kmeans.cluster_centers_
    except Exception as e:
        print(f"Clustering failed for user {user_id}: {e}")
        return np.mean(embeddings_np, axis=0).reshape(1, -1)

def calculate_chamfer_similarity(centroids1: np.ndarray, centroids2: np.ndarray) -> float:
    """
    Calculates asymmetric Chamfer Similarity between two sets of centroids.
    Sim(A, B) = (1/|A|) * sum_{a in A} max_{b in B} cosine_sim(a, b)
    Final metric is symmetric: (Sim(A, B) + Sim(B, A)) / 2
    """
    if centroids1 is None or centroids2 is None:
        return 0.0
        
    def one_way_chamfer(set_a, set_b):
        # set_a: (N, D), set_b: (M, D)
        # Normalize first for cosine similarity
        norm_a = np.linalg.norm(set_a, axis=1, keepdims=True)
        norm_b = np.linalg.norm(set_b, axis=1, keepdims=True)
        
        # Avoid division by zero
        norm_a[norm_a == 0] = 1e-9
        norm_b[norm_b == 0] = 1e-9
        
        a_normalized = set_a / norm_a
        b_normalized = set_b / norm_b
        
        # Similarity Matrix: (N, M)
        sim_matrix = np.dot(a_normalized, b_normalized.T)
        
        # For each centroid in A, find best matching centroid in B
        max_sims = np.max(sim_matrix, axis=1)
        return np.mean(max_sims) # Average of best matches

    sim_a_b = one_way_chamfer(centroids1, centroids2)
    sim_b_a = one_way_chamfer(centroids2, centroids1)
    
    return (sim_a_b + sim_b_a) / 2

import faiss
import pickle

# Global In-Memory Index (In production, this would be a standalone Vector DB like Milvus/Pinecone)
# We use IndexIDMap2 to map vectors back to User IDs
USER_INDEX = None
USER_DIMENSION = 1024

def build_user_index(db: Session):
    """
    Builds (or rebuilds) the FAISS index for all users in the database.
    This should be called periodically or on startup.
    """
    global USER_INDEX
    
    print("Building User FAISS Index...")
    users = db.query(models.User).all()
    
    # We need an index that supports ID mapping. 
    # IndexFlatIP (Inner Product) corresponds to Cosine Similarity if normalized.
    quantizer = faiss.IndexFlatIP(USER_DIMENSION)
    index = faiss.IndexIDMap2(quantizer)
    
    all_vectors = []
    all_ids = []
    
    count = 0
    for user in users:
        # Calculate centroids (N centroids per user)
        # Note: This calls DB per user, which is slow for huge N. 
        # In production, we'd use batch processing.
        centroids = calculate_user_vector(db, user.id)
        
        if centroids is not None:
            # centroids shape: (K, 768)
            # Add each centroid to the index with the SAME User ID
            # This means one User ID corresponds to multiple vectors in the space.
            k = centroids.shape[0]
            
            # Normalize for Cosine Similarity
            norms = np.linalg.norm(centroids, axis=1, keepdims=True)
            norms[norms == 0] = 1e-9
            normalized_centroids = centroids / norms
            
            all_vectors.append(normalized_centroids.astype('float32'))
            all_ids.extend([user.id] * k)
            count += 1
            
    if all_vectors:
        big_matrix = np.vstack(all_vectors)
        id_array = np.array(all_ids, dtype=np.int64)
        
        print(f"Debug: Adding vectors of shape {big_matrix.shape} to index of dim {USER_DIMENSION}")
        index.add_with_ids(big_matrix, id_array)
        USER_INDEX = index
        print(f"User Index built! Indexed {count} users with {index.ntotal} vectors.")
    else:
        print("No user data found to index.")

def get_similar_users(db: Session, current_user_id: int, limit: int = 5) -> List[Dict]:
    """
    Finds users with similar taste clusters using Scalable Hybrid Retrieval.
    1. Retrieval: Use FAISS to find candidates who share *any* similar cluster.
    2. Re-ranking: Calculate exact Chamfer Distance on candidates.
    """
    # 0. Ensure Index Exists (Lazy Load for Prototype)
    if USER_INDEX is None:
        build_user_index(db)
        
    # 1. Calculate current user's clusters
    current_user_clusters = calculate_user_vector(db, current_user_id)
    
    if current_user_clusters is None:
        return []

    # Get current user to find who they are following
    current_user = db.query(models.User).filter(models.User.id == current_user_id).first()
    following_ids = set([u.id for u in current_user.following] if current_user else [])
    following_ids.add(current_user_id) # Exclude self too

    # 2. Candidate Retrieval (Vector Search)
    candidates = set()
    
    if USER_INDEX is not None and USER_INDEX.ntotal > 0:
        # Query using ALL of my clusters
        # If I have 3 clusters, I search for neighbors for EACH cluster.
        k_neighbors = 20 # Retrieve top 20 matches per cluster
        
        # Normalize query
        norms = np.linalg.norm(current_user_clusters, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        query_vectors = (current_user_clusters / norms).astype('float32')
        
        distances, indices = USER_INDEX.search(query_vectors, k_neighbors)
        
        # Collect User IDs from results
        # indices shape: (n_clusters, k_neighbors)
        for row in indices:
            for retrieved_id in row:
                if retrieved_id != -1 and retrieved_id not in following_ids:
                    candidates.add(int(retrieved_id))
    
    # Fallback if index failed or empty, scan all (only for small scale)
    if not candidates and (USER_INDEX is None or USER_INDEX.ntotal == 0):
        all_users = db.query(models.User).filter(models.User.id.notin_(list(following_ids))).all()
        candidates = {u.id for u in all_users}

    print(f"Re-ranking {len(candidates)} candidates...")

    # 3. Re-ranking (Exact Chamfer Distance)
    similarities = []
    
    # Batch fetch candidates would be better, but loop is fine for N=100
    for user_id in candidates:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user: 
            continue
            
        other_user_clusters = calculate_user_vector(db, user_id)
        
        if other_user_clusters is not None:
            score = calculate_chamfer_similarity(current_user_clusters, other_user_clusters)
            
            if score > 0.0: 
                similarities.append({
                    "user": user,
                    "similarity": float(score)
                })

    # 4. Sort by similarity (descending)
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    
    return similarities[:limit]

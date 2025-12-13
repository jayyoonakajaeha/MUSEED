import faiss
import numpy as np
import os
import json
from tqdm import tqdm
import argparse

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # MUSEED/research -> MUSEED

# Default relative paths
DATA_ROOT = os.getenv("MUSEED_DATA_ROOT", os.path.join(BASE_DIR, "../data"))
MODELS_ROOT = os.getenv("MUSEED_MODELS_ROOT", os.path.join(BASE_DIR, "../models"))

# Unified embeddings directory
EMBEDDING_DIR = os.path.join(DATA_ROOT, 'embeddings_contrastive_v2_mean')
# Output paths for the generated index and its metadata
FAISS_INDEX_PATH = os.path.join(MODELS_ROOT, 'faiss_index.bin')
TRACK_IDS_PATH = os.path.join(MODELS_ROOT, 'faiss_track_ids.json')

def build_index():
    """
    Builds a FAISS index from the audio embeddings.
    """
    print("--- Starting FAISS Index Construction ---")

    # 1. Scan directory for valid .npy files
    print(f"Scanning embeddings from {EMBEDDING_DIR}...")
    
    if not os.path.exists(EMBEDDING_DIR):
        print(f"FATAL: Embedding directory not found at {EMBEDDING_DIR}")
        return

    npy_files = [f for f in os.listdir(EMBEDDING_DIR) if f.endswith('.npy')]
    npy_files.sort() # Ensure deterministic order by filename (track_id)
    
    print(f"Found {len(npy_files)} embedding files.")

    # 2. Load embeddings
    all_embeddings = []
    final_track_ids = []
    embedding_dim = -1

    for filename in tqdm(npy_files, desc="Loading embeddings"):
        # Extract track_id from filename (12345.npy -> 12345)
        try:
            track_id = int(os.path.splitext(filename)[0])
        except ValueError:
            print(f"Skipping file {filename}: filename is not a valid integer track_id")
            continue

        embedding_path = os.path.join(EMBEDDING_DIR, filename)
        try:
            embedding = np.load(embedding_path).astype('float32')
            if embedding.ndim != 1:
                print(f"Skipping track {track_id}: embedding is not 1D (shape: {embedding.shape})")
                continue
            
            if embedding_dim == -1:
                embedding_dim = embedding.shape[0]
            
            if embedding.shape[0] != embedding_dim:
                print(f"Skipping track {track_id}: inconsistent embedding dimension. Expected {embedding_dim}, got {embedding.shape[0]}")
                continue

            all_embeddings.append(embedding)
            final_track_ids.append(track_id)
        except Exception as e:
            print(f"Warning: Could not load embedding for track {track_id}: {e}")
    
    if not all_embeddings:
        print("FATAL: No embeddings were loaded. Cannot build index.")
        return

    embeddings_matrix = np.array(all_embeddings)
    print(f"Loaded {embeddings_matrix.shape[0]} embeddings with dimension {embeddings_matrix.shape[1]}.")

    # 3. Build the FAISS index
    print("\nBuilding FAISS index...")
    # Using IndexFlatIP because cosine similarity is dot product on normalized vectors.
    # Our embeddings should be normalized for this to be effective.
    index = faiss.IndexFlatIP(embedding_dim)
    
    # Normalize the embeddings before adding to the IndexFlatIP index
    faiss.normalize_L2(embeddings_matrix)
    
    index.add(embeddings_matrix)
    print(f"Index built successfully. Total vectors in index: {index.ntotal}")

    # 4. Save the index and the corresponding track IDs
    print(f"Saving FAISS index to {FAISS_INDEX_PATH}...")
    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"Saving track ID metadata to {TRACK_IDS_PATH}...")
    with open(TRACK_IDS_PATH, 'w') as f:
        json.dump(final_track_ids, f)

    print("\n--- FAISS Index Construction Complete! ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build a FAISS index from audio embeddings.")
    parser.parse_args() # No arguments needed, just runs the build
    build_index()

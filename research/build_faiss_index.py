import faiss
import numpy as np
import os
import json
from tqdm import tqdm
import argparse

# --- Configuration ---
# Use the fine-tuned embeddings as they performed better in evaluation
EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings_finetuned_muq/' 
# The JSONL file provides the list and order of tracks to be indexed
JSONL_PATH = '/home/jay/MusicAI/multi_axis_analysis_results.jsonl' 
# Output paths for the generated index and its metadata
FAISS_INDEX_PATH = 'faiss_index.bin'
TRACK_IDS_PATH = 'faiss_track_ids.json'

def build_index():
    """
    Builds a FAISS index from the audio embeddings.
    """
    print("--- Starting FAISS Index Construction ---")

    # 1. Load track IDs from the JSONL file to ensure order
    print(f"Loading track order from {JSONL_PATH}...")
    try:
        track_ids_in_order = []
        with open(JSONL_PATH, 'r') as f:
            for line in f:
                track_ids_in_order.append(json.loads(line)['track_id'])
    except FileNotFoundError:
        print(f"FATAL: Metadata file not found at {JSONL_PATH}. Cannot determine track order.")
        return

    # 2. Load embeddings into a single numpy array
    print(f"Loading embeddings from {EMBEDDING_DIR}...")
    all_embeddings = []
    final_track_ids = []
    embedding_dim = -1

    for track_id in tqdm(track_ids_in_order, desc="Loading embeddings"):
        embedding_path = os.path.join(EMBEDDING_DIR, f"{track_id}.npy")
        if os.path.exists(embedding_path):
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

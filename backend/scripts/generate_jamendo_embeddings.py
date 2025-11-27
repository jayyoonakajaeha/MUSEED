import os
import sys
import json
import numpy as np
import torch
import torchaudio
import faiss
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import models, database
from muq import MuQ

# Configuration
JAMENDO_DIR = "/home/jay/MusicAI/jamendo_downloads"
EMBEDDING_DIR = "/home/jay/MusicAI/fma_audio_embeddings_finetuned_muq"
FAISS_INDEX_PATH = "faiss_index.bin"
TRACK_IDS_PATH = "faiss_track_ids.json"
FINETUNED_MODEL_PATH = "/home/jay/MusicAI/MuQ/finetuned_models/muq_finetuned_triplet_float32.pth"
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000  # 10 seconds

def get_db_session():
    engine = database.engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def process_audio(file_path):
    try:
        waveform, sr = torchaudio.load(file_path)
        if sr != SAMPLE_RATE:
            waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        if waveform.shape[1] < DURATION_SAMPLES:
            waveform = torch.nn.functional.pad(waveform, (0, DURATION_SAMPLES - waveform.shape[1]))
        else:
            # Center crop roughly
            start = (waveform.shape[1] - DURATION_SAMPLES) // 2
            waveform = waveform[:, start:start + DURATION_SAMPLES]
        
        return waveform
    except Exception as e:
        print(f"Error loading audio {file_path}: {e}")
        return None

def main():
    print(f"Using device: {DEVICE}")
    
    # 1. Load DB and get Jamendo tracks
    db = get_db_session()
    jamendo_tracks = db.query(models.Track).filter(models.Track.track_id >= 200000).all()
    print(f"Found {len(jamendo_tracks)} Jamendo tracks in DB.")
    
    # 2. Load existing FAISS index and map
    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading existing FAISS index...")
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        print("Creating new FAISS index...")
        index = faiss.IndexFlatIP(768) # Inner Product (Cosine Similarity after normalization)

    if os.path.exists(TRACK_IDS_PATH):
        print("Loading track ID map...")
        with open(TRACK_IDS_PATH, 'r') as f:
            track_id_map = json.load(f)
    else:
        track_id_map = []

    # Convert map to set for fast lookup of existing IDs (as strings for consistency)
    existing_ids = set(map(str, track_id_map))
    
    # 3. Load Model
    print("Loading MuQ model...")
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)
    model.load_state_dict(torch.load(FINETUNED_MODEL_PATH, map_location=DEVICE))
    model.eval()
    
    # 4. Process Tracks
    new_vectors = []
    new_ids = []
    
    for track in tqdm(jamendo_tracks, desc="Processing tracks"):
        track_id_str = str(track.track_id)
        
        # Check if we already have the .npy file
        embedding_path = os.path.join(EMBEDDING_DIR, f"{track.track_id}.npy")
        
        embedding = None
        
        # If already in FAISS and file exists, skip
        if track_id_str in existing_ids and os.path.exists(embedding_path):
            continue

        # Construct file path
        filename = f"{track.artist_name} - {track.title}.mp3"
        file_path = os.path.join(JAMENDO_DIR, filename)
        
        if not os.path.exists(file_path):
            # Try glob match if exact match fails
            import glob
            candidates = glob.glob(os.path.join(JAMENDO_DIR, f"*{track.title}*.mp3"))
            if candidates:
                file_path = candidates[0]
            else:
                print(f"Audio file not found for {track.title}")
                continue

        # Generate embedding if needed
        if not os.path.exists(embedding_path):
            waveform = process_audio(file_path)
            if waveform is None:
                continue
            
            waveform = waveform.to(DEVICE).unsqueeze(0) # Batch dim
            
            with torch.no_grad():
                emb = model(waveform).last_hidden_state[:, 0, :].cpu().numpy().flatten()
            
            # Save .npy
            np.save(embedding_path, emb)
            embedding = emb
        else:
            # Load existing .npy
            embedding = np.load(embedding_path)

        # Add to new lists if not in FAISS
        if track_id_str not in existing_ids:
            # Normalize for Cosine Similarity
            faiss.normalize_L2(embedding.reshape(1, -1))
            new_vectors.append(embedding)
            new_ids.append(track.track_id)

    # 5. Update Index and Map
    if new_vectors:
        print(f"Adding {len(new_vectors)} new vectors to FAISS index...")
        new_vectors_np = np.vstack(new_vectors).astype('float32')
        index.add(new_vectors_np)
        track_id_map.extend(new_ids)
        
        print("Saving updated index and map...")
        faiss.write_index(index, FAISS_INDEX_PATH)
        with open(TRACK_IDS_PATH, 'w') as f:
            json.dump(track_id_map, f)
        print("Done.")
    else:
        print("No new tracks to add.")

if __name__ == "__main__":
    main()

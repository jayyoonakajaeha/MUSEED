import faiss
import numpy as np
import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import io

# Add imports for model loading and audio processing
import torch
import torchaudio
from muq import MuQ

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

# --- Router Setup ---
router = APIRouter(
    prefix="/api/playlists",
    tags=["playlists"]
)

# --- Configuration & Global Variables ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings_finetuned_muq/'
NUM_RECOMMENDATIONS = 15
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000  # 10 seconds

# --- FAISS Index Loading ---
FAISS_INDEX_PATH = 'faiss_index.bin'
TRACK_IDS_PATH = 'faiss_track_ids.json'
faiss_index = None
track_id_map = None

# --- Model Loading ---
FINETUNED_MODEL_PATH = '/home/jay/MusicAI/MuQ/finetuned_models/muq_finetuned_triplet_float32.pth'
model = None

# Load all assets at startup
try:
    print("Loading FAISS index...")
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    print(f"FAISS index loaded successfully. Index contains {faiss_index.ntotal} vectors.")
    
    print("Loading track ID map...")
    with open(TRACK_IDS_PATH, 'r') as f:
        track_id_map = json.load(f)
    print("Track ID map loaded successfully.")

    print(f"Loading fine-tuned MuQ model from {FINETUNED_MODEL_PATH}...")
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)
    model.load_state_dict(torch.load(FINETUNED_MODEL_PATH, map_location=DEVICE))
    model.eval()
    print("MuQ model loaded successfully.")

except FileNotFoundError as e:
    print(f"WARNING: Asset file not found: {e}. Playlist generation will not work.")
    faiss_index = None
    track_id_map = None
    model = None
except Exception as e:
    print(f"An error occurred during asset loading: {e}")
    faiss_index = None
    track_id_map = None
    model = None

# --- Helper Functions ---
def process_uploaded_audio(audio_bytes: bytes) -> torch.Tensor:
    """Loads audio from bytes, resamples, and trims/pads to the required duration."""
    try:
        waveform, sr = torchaudio.load(io.BytesIO(audio_bytes))
        if sr != SAMPLE_RATE:
            waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        if waveform.shape[1] < DURATION_SAMPLES:
            waveform = torch.nn.functional.pad(waveform, (0, DURATION_SAMPLES - waveform.shape[1]))
        else:
            start = (waveform.shape[1] - DURATION_SAMPLES) // 2
            waveform = waveform[:, start:start + DURATION_SAMPLES]
        return waveform
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process uploaded audio file: {e}")


# --- API Endpoints ---

@router.get("/discover", response_model=List[schemas.Playlist])
def get_discover_playlists(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a list of public playlists for the discover page.
    """
    playlists = crud.get_public_playlists(db, skip=skip, limit=limit)
    # Dynamically set whether the current user has liked each playlist
    for playlist in playlists:
        playlist.liked_by_user = current_user in playlist.liked_by
    return playlists

@router.get("/trending", response_model=List[schemas.Playlist])
def get_trending_playlists(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get trending playlists (most likes in last 24h).
    """
    playlists = crud.get_trending_playlists(db, limit=limit)
    for playlist in playlists:
        playlist.liked_by_user = current_user in playlist.liked_by
    return playlists

@router.get("/search", response_model=List[schemas.Playlist])
def search_for_playlists(
    q: Optional[str] = Query(None, min_length=2),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if q is None:
        return []
    playlists = crud.search_playlists(db, query=q, skip=skip, limit=limit)
    for playlist in playlists:
        playlist.liked_by_user = current_user in playlist.liked_by
    return playlists

@router.post("/upload", response_model=schemas.Playlist)
async def create_ai_playlist_from_upload(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not all([faiss_index, track_id_map, model]):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required AI model or index is not available.",
        )

    # 1. Process the uploaded audio file
    audio_bytes = await file.read()
    waveform = process_uploaded_audio(audio_bytes)
    waveform = waveform.to(DEVICE)

    # 2. Generate embedding on the fly
    with torch.no_grad():
        seed_embedding = model(waveform).last_hidden_state[:, 0, :]
    
    seed_embedding_numpy = seed_embedding.cpu().numpy()

    # 3. Normalize and search the index
    faiss.normalize_L2(seed_embedding_numpy)
    distances, indices = faiss_index.search(seed_embedding_numpy, NUM_RECOMMENDATIONS)

    # 4. Map indices back to track IDs
    found_track_ids = [track_id_map[i] for i in indices[0]]

    # 5. Create the playlist in the database
    new_playlist = crud.create_playlist(
        db=db,
        name=name,
        owner_id=current_user.id,
        track_ids=found_track_ids
    )

    return new_playlist


@router.post("/", response_model=schemas.Playlist)
def create_ai_playlist_from_id(
    playlist_in: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not faiss_index or not track_id_map:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="FAISS index is not available. Cannot generate playlist.",
        )

    # 1. Get the embedding for the seed track
    seed_track_id = playlist_in.seed_track_id
    embedding_path = os.path.join(EMBEDDING_DIR, f"{seed_track_id}.npy")
    
    if not os.path.exists(embedding_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding for seed track ID '{seed_track_id}' not found.",
        )
    
    try:
        seed_embedding = np.load(embedding_path).astype('float32')
        if seed_embedding.ndim != 1:
            raise ValueError("Invalid embedding dimension")
        seed_embedding = np.expand_dims(seed_embedding, axis=0) # Add batch dimension
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load or process seed embedding: {e}",
        )

    # 2. Normalize the seed embedding and search the index
    faiss.normalize_L2(seed_embedding)
    
    # Search for N+1 tracks because the seed track itself will be the top result
    distances, indices = faiss_index.search(seed_embedding, NUM_RECOMMENDATIONS + 1)

    # 3. Map indices back to track IDs
    found_track_ids = [track_id_map[i] for i in indices[0]]

    # 4. Create the final track list, excluding the seed track itself if it's in the results
    final_track_ids = [seed_track_id]
    for found_id in found_track_ids:
        if str(found_id) != str(seed_track_id):
            final_track_ids.append(str(found_id))
    
    # Ensure we have the correct number of tracks
    final_track_ids = final_track_ids[:NUM_RECOMMENDATIONS + 1]

    # 5. Create the playlist in the database
    new_playlist = crud.create_playlist(
        db=db,
        name=playlist_in.name,
        owner_id=current_user.id,
        track_ids=final_track_ids
    )

    return new_playlist

@router.get("/{playlist_id}", response_model=schemas.Playlist)
def read_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Set liked_by_user dynamically
    db_playlist.liked_by_user = current_user in db_playlist.liked_by
    
    return db_playlist

@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this playlist")
    
    crud.delete_playlist(db, playlist_id=playlist_id)
    return {"message": "Playlist deleted successfully"}

@router.put("/{playlist_id}", response_model=schemas.Playlist)
def update_playlist(
    playlist_id: int,
    playlist_update: schemas.PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if db_playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this playlist")
    
    updated_playlist = crud.update_playlist(db, playlist_id=playlist_id, playlist_update=playlist_update)
    if updated_playlist is None:
        raise HTTPException(status_code=500, detail="Failed to update playlist")
    
    updated_playlist.liked_by_user = current_user in updated_playlist.liked_by
    
    return updated_playlist

@router.post("/{playlist_id}/like", response_model=schemas.Playlist)
def like_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.like_playlist(db, playlist_id=playlist_id, user_id=current_user.id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    db_playlist.liked_by_user = True # User just liked it
    
    return db_playlist

@router.delete("/{playlist_id}/like", response_model=schemas.Playlist)
def unlike_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_playlist = crud.unlike_playlist(db, playlist_id=playlist_id, user_id=current_user.id)
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    db_playlist.liked_by_user = False # User just unliked it
    
    return db_playlist

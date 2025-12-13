
import os
import io
import json
import torch
import faiss
import numpy as np
import random
import librosa
from .worker import celery_app
from . import crud, schemas, models
from .database import SessionLocal  
from muq import MuQ

# --- Constants & Paths ---
# --- Constants & Paths (Environment Aware) ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

if os.path.exists('/app/models'):
    # Docker Environment
    EMBEDDING_DIR = '/app/data/embeddings'
    FAISS_INDEX_PATH = '/app/models/faiss_index.bin'
    TRACK_IDS_PATH = '/app/models/faiss_track_ids.json'
    FINETUNED_MODEL_PATH = '/app/models/muq_contrastive_simclr_v2.pth'
else:
    # Local/Host Environment
    # Use relative paths or env vars to avoid hardcoding specific user home dir
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # MUSEED/backend/app -> MUSEED/backend -> MUSEED
    
    # Default relative paths: Sibling directories (MusicAI_Workspace/data, MusicAI_Workspace/models)
    DATA_ROOT = os.getenv("MUSEED_DATA_ROOT", os.path.join(BASE_DIR, "../data")) # ../MUSEED/data -> MusicAI/data
    MODELS_ROOT = os.getenv("MUSEED_MODELS_ROOT", os.path.join(BASE_DIR, "../models")) # ../MUSEED/models -> MusicAI/models

    EMBEDDING_DIR = os.path.join(DATA_ROOT, 'embeddings_contrastive_v2_mean')
    FAISS_INDEX_PATH = os.path.join(MODELS_ROOT, 'faiss_index.bin')
    TRACK_IDS_PATH = os.path.join(MODELS_ROOT, 'faiss_track_ids.json')
    FINETUNED_MODEL_PATH = os.path.join(MODELS_ROOT, 'muq_contrastive_simclr_v2.pth')
NUM_RECOMMENDATIONS = 15
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000

# --- 전역 리소스 (워커당 한 번 로드) ---
faiss_index = None
track_id_map = None
model = None

def load_resources():
    global faiss_index, track_id_map, model
    if model is not None:
        return

    print("Worker: AI 리소스 로딩 중...")
    try:
        if os.path.exists(FAISS_INDEX_PATH):
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            print(f"Worker: FAISS 인덱스 로드됨 ({faiss_index.ntotal} 벡터).")
        
        if os.path.exists(TRACK_IDS_PATH):
            with open(TRACK_IDS_PATH, 'r') as f:
                track_id_map = json.load(f)
            print("Worker: 트랙 ID 맵 로드됨.")

        print(f"Worker: MuQ 모델 로딩 ({FINETUNED_MODEL_PATH})...")
        model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)
        model.load_state_dict(torch.load(FINETUNED_MODEL_PATH, map_location=DEVICE))
        
        if DEVICE == 'cuda':
            print("Worker: 모델 FP16 변환 중...")
            model.half()
            
        model.eval()
        print("Worker: MuQ 모델 로드 완료.")

    except Exception as e:
        print(f"Worker: 리소스 로드 실패: {e}")
        # 여기서 에러 발생시키지 않음, 태스크별로 처리

# 모듈 임포트 시(워커 시작) 리소스 사전 로드
# Optimization: Only load if running as a Celery Worker (prevent double-loading in Backend API)
if os.getenv("IS_CELERY_WORKER") == "true":
    print("[TASKS] Celery Worker detected. Loading resources...")
    load_resources()
else:
    print("[TASKS] Backend API detected. Skipping resource load.")

# --- 헬퍼 함수 ---
def process_audio_for_embedding(audio_path: str) -> torch.Tensor:
    print(f"[TASKS] Processing audio: {audio_path}")
    try:
        # Use Librosa for robust MP3 support and automatic resampling/mono conversion
        # librosa.load automatically resamples to sr=sr if provided, and mixes to mono by default.
        # Optimization: Read metadata first to get duration
        try:
             duration = librosa.get_duration(path=audio_path)
        except Exception:
             duration = 0 # Fallback
        
        target_sec = DURATION_SAMPLES / SAMPLE_RATE # 10 seconds
        
        if duration > target_sec:
            # 1. Center Crop
            offset_center = (duration - target_sec) / 2
            
            # 2. Random Crop (Non-overlapping)
            # Valid range: [0, duration - target_sec] excluding [offset_center - target_sec, offset_center + target_sec]
            # Simplification: Pick from [0, offset_center - target_sec] OR [offset_center + target_sec, duration - target_sec]
            import random
            candidates = []
            if offset_center - target_sec > 0:
                candidates.append((0, offset_center - target_sec))
            if offset_center + target_sec < duration - target_sec:
                candidates.append((offset_center + target_sec, duration - target_sec))
            
            offset_random = None
            if candidates:
                start, end = random.choice(candidates)
                offset_random = random.uniform(start, end)
            
            # Load Center
            import time
            t0 = time.time()
            y_center, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True, offset=offset_center, duration=target_sec)
            
            # Load Random (if possible)
            y_random = None
            if offset_random is not None:
                y_random, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True, offset=offset_random, duration=target_sec)
                
            print(f"[TASKS] efficient_load: Center={offset_center:.2f}s, Random={offset_random if offset_random else 'None'}")
            
            # Stack
            waveforms = [torch.from_numpy(y_center)]
            if y_random is not None:
                 waveforms.append(torch.from_numpy(y_random))
                 
            # Pad
            padded_waveforms = []
            for w in waveforms:
                 if w.shape[0] < DURATION_SAMPLES:
                      w = torch.nn.functional.pad(w, (0, DURATION_SAMPLES - w.shape[0]))
                 padded_waveforms.append(w)
            
            # Stack into (N, samples)
            batch = torch.stack(padded_waveforms)
            return batch
            
        else:
             # Short file: load all, pad
             y, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
             w = torch.from_numpy(y)
             if w.shape[0] < DURATION_SAMPLES:
                  w = torch.nn.functional.pad(w, (0, DURATION_SAMPLES - w.shape[0]))
             return w.unsqueeze(0)

    except Exception as e:
        print(f"[TASKS] Audio processing failed: {e}")
        raise ValueError(f"Processing failed: {e}")

# --- Tasks ---

@celery_app.task(bind=True)
def generate_playlist_task(self, name: str, file_path: str, owner_id: int):
    """
    AI 플레이리스트 생성 (업로드 기반)
    Steps:
    1. 오디오 로드 및 전처리 (Center + Random Crop)
    2. MuQ 임베딩 추출 (Mean Pooling)
    3. FAISS 검색
    4. DB 플레이리스트 생성
    """
    print(f"[TASKS] Task Started. File: {file_path}")
    if not os.path.exists(file_path):
        print(f"[TASKS] File not found: {file_path}")
        return {"success": False, "error": "File not found"}

    # Worker context check
    if not all([model, faiss_index, track_id_map]):
        print("[TASKS] Models not loaded (Startup failed?).")
        return {"success": False, "error": "AI Models not loaded in worker."}

    db = SessionLocal()
    try:
        # 1. 오디오 처리
        print("[TASKS] Step 1: Process Audio")
        # Returns (N, Samples) where N=1 or 2
        input_tensor = process_audio_for_embedding(file_path).to(DEVICE)
        if DEVICE == 'cuda':
            input_tensor = input_tensor.half()
        
        # 2. 추론
        print(f"[TASKS] Step 2: Inference (Batch Size: {input_tensor.shape[0]})")
        with torch.no_grad():
            embeddings = model(input_tensor).last_hidden_state[:, 0, :] # (N, 1024)
            
        # Mean Pool if N > 1
        if embeddings.shape[0] > 1:
             seed_embedding = torch.mean(embeddings, dim=0, keepdim=True) # (1, 1024)
        else:
             seed_embedding = embeddings
             
        seed_embedding_numpy = seed_embedding.float().cpu().numpy() # FAISS용 float32 변환
        
        # 3. 검색
        print("[TASKS] Step 3: Search")
        faiss.normalize_L2(seed_embedding_numpy)
        distances, indices = faiss_index.search(seed_embedding_numpy, NUM_RECOMMENDATIONS)
        found_track_ids = [track_id_map[i] for i in indices[0]]
        
        # 4. DB 저장
        # owner_id는 비로그인 시 None일 수 있음
        
        print("[TASKS] Validating Track IDs against DB...")
        # FAISS might return IDs that don't exist in DB (integrity mismatch).
        # Filter them out to prevent FK violation.
        valid_rows = db.query(models.Track.track_id).filter(models.Track.track_id.in_(found_track_ids)).all()
        valid_ids_set = set(row[0] for row in valid_rows)
        
        final_track_ids = [tid for tid in found_track_ids if tid in valid_ids_set]
        
        print(f"[TASKS] Found {len(found_track_ids)} tracks, {len(final_track_ids)} are valid.")
        
        if not final_track_ids:
             print("[TASKS] No valid tracks found.")
             if os.path.exists(file_path): os.remove(file_path)
             return {"success": False, "error": "No similar tracks found in database."}
        
        print(f"[TASKS] Step 4: DB Save (Owner: {owner_id})")
        new_playlist = crud.create_playlist(
            db=db,
            name=name,
            owner_id=owner_id,
            track_ids=final_track_ids
        )
        
        # 임시 파일 정리
        print("[TASKS] Cleanup")
        if os.path.exists(file_path):
            os.remove(file_path)
            
        print(f"[TASKS] Success. Playlist ID: {new_playlist.id}")
        return {"success": True, "playlist_id": new_playlist.id}

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task
def generate_playlist_from_id_task(name: str, seed_track_id: int, owner_id: int):
    """
    ID 기반 플레이리스트 생성 백그라운드 태스크
    """
    global faiss_index, track_id_map
    # 모델은 필요 없지만 FAISS 인덱스는 필수
    
    if not all([faiss_index, track_id_map]):
         return {"success": False, "error": "FAISS Index not loaded."}

    db = SessionLocal()
    try:
        embedding_path = os.path.join(EMBEDDING_DIR, f"{seed_track_id}.npy")
        if not os.path.exists(embedding_path):
            return {"success": False, "error": f"Embedding for {seed_track_id} not found."}
            
        seed_embedding = np.load(embedding_path).astype('float32')
        if seed_embedding.ndim == 1:
            seed_embedding = np.expand_dims(seed_embedding, axis=0)
            
        faiss.normalize_L2(seed_embedding)
        distances, indices = faiss_index.search(seed_embedding, NUM_RECOMMENDATIONS + 1)
        
        found_track_ids = [track_id_map[i] for i in indices[0]]
        final_track_ids = [seed_track_id]
        for found_id in found_track_ids:
            if str(found_id) != str(seed_track_id):
                final_track_ids.append(found_id)
        
        final_track_ids = final_track_ids[:NUM_RECOMMENDATIONS + 1]

        new_playlist = crud.create_playlist(
            db=db,
            name=name,
            owner_id=owner_id,
            track_ids=final_track_ids
        )
        return {"success": True, "playlist_id": new_playlist.id}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()

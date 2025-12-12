
import os
import io
import json
import torch
import torchaudio
import faiss
import numpy as np
import random
from .worker import celery_app
from . import crud, schemas, models
from .database import SessionLocal  
from muq import MuQ

# --- Constants & Paths ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
EMBEDDING_DIR = '/home/jay/MusicAI/MUSEED/data/embeddings_contrastive_v2_mean/'
FAISS_INDEX_PATH = '/home/jay/MusicAI/MUSEED/models/faiss_index.bin'
TRACK_IDS_PATH = '/home/jay/MusicAI/MUSEED/models/faiss_track_ids.json'
FINETUNED_MODEL_PATH = '/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v2.pth'
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
load_resources()

# --- 헬퍼 함수 ---
def process_audio_for_embedding(audio_path: str) -> torch.Tensor:
    try:
        waveform, sr = torchaudio.load(audio_path)
        
        if sr != SAMPLE_RATE:
            waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
        
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0)
        else:
            waveform = waveform.squeeze(0)

        total_samples = waveform.shape[0]
        
        if total_samples < DURATION_SAMPLES:
            waveform = torch.nn.functional.pad(waveform, (0, DURATION_SAMPLES - total_samples))
            return waveform.unsqueeze(0)
            
        center_start = (total_samples - DURATION_SAMPLES) // 2
        center_end = center_start + DURATION_SAMPLES
        center_crop = waveform[center_start : center_end]
        
        return center_crop.unsqueeze(0) # Simplify to just Center Crop for stability

    except Exception as e:
        raise ValueError(f"Processing failed: {e}")

# --- Tasks ---

@celery_app.task
def generate_playlist_task(name: str, file_path: str, owner_id: int):
    """
    업로드된 파일 기반 플레이리스트 생성 백그라운드 태스크
    """
    global model, faiss_index, track_id_map
    if not all([model, faiss_index, track_id_map]):
        load_resources() # 재시도
        if not all([model, faiss_index, track_id_map]):
            return {"success": False, "error": "AI Models not loaded in worker."}

    db = SessionLocal()
    try:
        # 1. 오디오 처리
        input_tensor = process_audio_for_embedding(file_path).to(DEVICE)
        if DEVICE == 'cuda':
            input_tensor = input_tensor.half()
        
        # 2. 추론
        with torch.no_grad():
            seed_embedding = model(input_tensor).last_hidden_state[:, 0, :]
        seed_embedding_numpy = seed_embedding.float().cpu().numpy() # FAISS용 float32 변환
        
        # 3. 검색
        faiss.normalize_L2(seed_embedding_numpy)
        distances, indices = faiss_index.search(seed_embedding_numpy, NUM_RECOMMENDATIONS)
        found_track_ids = [track_id_map[i] for i in indices[0]]
        
        # 4. DB 저장
        # owner_id는 비로그인 시 None일 수 있음
        
        new_playlist = crud.create_playlist(
            db=db,
            name=name,
            owner_id=owner_id,
            track_ids=found_track_ids
        )
        
        # 임시 파일 정리
        if os.path.exists(file_path):
            os.remove(file_path)
            
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


import torch
import pandas as pd
import torchaudio
import os
import numpy as np
from muq import MuQMuLan
from tqdm import tqdm
import random

# --- 설정 ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TRACKS_CSV_PATH = '/home/jay/MusicAI/fma/data/fma_metadata/track_toplevel_genres.csv'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings/' # 임베딩을 저장할 디렉토리
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000 # 10초

# 오디오 로딩 함수
def load_audio_segment(track_id, audio_dir):
    track_id_str = f"{track_id:06d}"
    file_path = os.path.join(audio_dir, track_id_str[:3], track_id_str + '.mp3')
    try:
        waveform, sr = torchaudio.load(file_path)
        if sr != SAMPLE_RATE:
            waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if waveform.shape[1] < DURATION_SAMPLES:
            waveform = torch.nn.functional.pad(waveform, (0, DURATION_SAMPLES - waveform.shape[1]))
        else:
            start = random.randint(0, waveform.shape[1] - DURATION_SAMPLES)
            waveform = waveform[:, start:start + DURATION_SAMPLES]
        return waveform
    except Exception as e:
        print(f"Warning: Could not load or process {file_path}. Error: {e}. Skipping track.")
        return None

def main():
    print(f"Using device: {DEVICE}")

    # --- 출력 디렉토리 생성 ---
    print(f"Ensuring embedding directory exists at: {EMBEDDING_DIR}")
    os.makedirs(EMBEDDING_DIR, exist_ok=True)

    # --- 모델 로드 ---
    print("Loading MuQ-MuLan model...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(DEVICE).eval()

    # --- 트랙 목록 로드 ---
    print(f"Loading track list from {TRACKS_CSV_PATH}...")
    try:
        tracks_df = pd.read_csv(TRACKS_CSV_PATH)
        track_ids = tracks_df['track_id'].tolist()
    except FileNotFoundError:
        print(f"Error: Track CSV file not found at {TRACKS_CSV_PATH}. Aborting.")
        return

    # --- 메인 루프: 각 트랙의 임베딩 추출 및 저장 ---
    print(f"Starting embedding extraction for {len(track_ids)} tracks...")
    print(f"Embeddings will be saved in: {EMBEDDING_DIR}")

    for track_id in tqdm(track_ids, desc="Extracting Embeddings"):
        embedding_path = os.path.join(EMBEDDING_DIR, f"{track_id}.npy")

        # 이미 파일이 존재하면 건너뛰기 (이어서 실행 가능하도록)
        if os.path.exists(embedding_path):
            continue

        # 오디오 로드
        waveform = load_audio_segment(track_id, AUDIO_DIR)
        if waveform is None:
            continue
        
        waveform = waveform.to(DEVICE)

        # 오디오 임베딩 추출
        with torch.no_grad():
            audio_embed = model(wavs=waveform)
        
        # Numpy 배열로 변환하여 저장
        embedding_numpy = audio_embed.cpu().numpy()
        np.save(embedding_path, embedding_numpy)

    print("\n--- Embedding extraction complete! ---")
    print(f"All available track embeddings are saved in {EMBEDDING_DIR}")

if __name__ == '__main__':
    main()

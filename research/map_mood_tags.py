
import torch
import pandas as pd
import torchaudio
import random
import os
from torch.utils.data import Dataset, DataLoader
from muq import MuQMuLan
from tqdm import tqdm

# 1. 대표 분위기 태그 리스트 정의
MOOD_TAGS = [
    'energetic', 'upbeat', 'powerful',  # --- High Energy
    'calm', 'relaxing', 'peaceful', 'ambient', # --- Low Energy
    'happy', 'cheerful', 'bright',      # --- Positive Valence
    'sad', 'dark', 'melancholic', 'dramatic', # --- Negative Valence
    'romantic', 'love', 'sentimental', # --- Romantic
    'groovy', 'funky', 'danceable',    # --- Rhythmic/Dance
    'epic', 'orchestral', 'cinematic', # --- Grandiose
    'experimental', 'strange', 'minimalist' # --- Astract/Structural
]

# 오디오 로딩 및 전처리 함수 (fma_triplet_dataset.py에서 가져옴)
def load_audio_segment(track_id, audio_dir, sample_rate=16000, duration_samples=160000):
    track_id_str = f"{track_id:06d}"
    file_path = os.path.join(audio_dir, track_id_str[:3], track_id_str + '.mp3')
    try:
        waveform, sr = torchaudio.load(file_path)
        if sr != sample_rate:
            resampler = torchaudio.transforms.Resample(sr, sample_rate)
            waveform = resampler(waveform)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if waveform.shape[1] < duration_samples:
            padding = duration_samples - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
        else:
            start = random.randint(0, waveform.shape[1] - duration_samples)
            waveform = waveform[:, start:start + duration_samples]
        return waveform
    except Exception as e:
        print(f"Warning: Could not load or process {file_path}. Error: {e}. Skipping track.")
        return None

def main():
    # --- 설정 ---
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tracks_csv_path = '/home/jay/MusicAI/fma/data/fma_metadata/track_toplevel_genres.csv'
    audio_dir = '/home/jay/MusicAI/fma/data/fma_full'
    output_csv_path = '/home/jay/MusicAI/fma/data/fma_metadata/track_mood_tags.csv'
    sample_rate = 16000
    duration = 10 # 10초
    duration_samples = sample_rate * duration

    print(f"Using device: {device}")

    # --- 모델 로드 ---
    print("Loading MuQ-MuLan model...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(device).eval()

    # --- 데이터 로드 ---
    print(f"Loading track list from {tracks_csv_path}...")
    tracks_df = pd.read_csv(tracks_csv_path)
    track_ids = tracks_df['track_id'].tolist()

    # --- 텍스트 임베딩 미리 계산 (최적화) ---
    print("Calculating text embeddings for mood tags...")
    with torch.no_grad():
        text_embeds = model(texts=MOOD_TAGS).to(device)

    # --- 메인 루프: 각 트랙에 대해 태그 매핑 ---
    results = []
    print(f"Starting mood tagging for {len(track_ids)} tracks...")
    for track_id in tqdm(track_ids):
        # 오디오 로드 및 전처리
        waveform = load_audio_segment(track_id, audio_dir, sample_rate, duration_samples)
        if waveform is None:
            continue
        
        waveform = waveform.to(device)

        # 오디오 임베딩 추출
        with torch.no_grad():
            audio_embed = model(wavs=waveform)

        # 유사도 계산
        # (1, D) 형태의 오디오 임베딩과 (N_tags, D) 형태의 텍스트 임베딩 간의 유사도 계산
        similarity = torch.nn.functional.cosine_similarity(audio_embed, text_embeds, dim=-1)
        
        # 가장 유사한 태그 선택
        best_tag_index = torch.argmax(similarity).item()
        assigned_tag = MOOD_TAGS[best_tag_index]

        results.append({'track_id': track_id, 'mood_tag': assigned_tag})

    # --- 결과 저장 ---
    print("\n--- Tagging Complete! ---")
    if not results:
        print("No tracks were tagged. Please check your audio files and paths.")
        return

    output_df = pd.DataFrame(results)
    print(f"Saving results to {output_csv_path}...")
    output_df.to_csv(output_csv_path, index=False)

    print(f"Successfully tagged {len(output_df)} tracks.")
    print("\nSample of the final data:")
    print(output_df.head())

if __name__ == '__main__':
    main()

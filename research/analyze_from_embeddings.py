import torch
import pandas as pd
import os
import json
import numpy as np
from muq import MuQMuLan
from tqdm import tqdm

# --- 분석을 위한 태그 목록 정의 ---

# 2. 악기 소스 (어쿠스틱 vs 일렉트로닉)
INSTRUMENTATION_SOURCE_TAGS = [
    'acoustic sound, natural instruments, unplugged, raw, organic, live recording',
    'electronic sound, synthesized, processed, digital instruments, programmed beats, effects, modulated'
]

# 3-1: 감정가 (Valence)
VALENCE_TAGS = ['positive', 'bright', 'happy', 'cheerful', 'negative', 'dark', 'sad', 'angry']
POSITIVE_SUBGROUP = ['positive', 'bright', 'happy', 'cheerful']

# 3-2: 에너지 (Energy/Arousal)
ENERGY_TAGS = ['high energy', 'energetic', 'intense', 'medium energy', 'moderate', 'low energy', 'calm', 'relaxed', 'peaceful']
HIGH_ENERGY_SUBGROUP = ['high energy', 'energetic', 'intense']
LOW_ENERGY_SUBGROUP = ['low energy', 'calm', 'relaxed', 'peaceful']

# 4: 세부 분위기 (Fine-grained Mood)
MOOD_STYLE_TAGS = ['funky', 'groovy', 'sentimental', 'romantic', 'epic', 'cinematic', 'powerful', 'ambient', 'experimental', 'minimalist', 'strange', 'dark']

# --- 설정 ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TRACKS_CSV_PATH = '/home/jay/MusicAI/fma/data/fma_metadata/track_toplevel_genres.csv'
EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings/'
OUTPUT_JSONL_PATH = '/home/jay/MusicAI/MUSEED/data/multi_axis_analysis_results.jsonl'

# --- 유사도 계산 함수 ---
def get_best_tag(audio_embed, text_embeds, text_labels):
    similarity = torch.nn.functional.cosine_similarity(audio_embed, text_embeds, dim=-1)
    best_tag_index = torch.argmax(similarity).item()
    return text_labels[best_tag_index]

# --- 메인 분석 함수 ---
def analyze_embedding(track_id, audio_embed, genre, text_embeds_dict):
    # 2: 악기 소스 (어쿠스틱 vs 일렉트로닉)
    raw_source_tag = get_best_tag(audio_embed, text_embeds_dict['source'], INSTRUMENTATION_SOURCE_TAGS)

    # 설명 태그를 단순 'acoustic' 또는 'electronic'으로 매핑
    if raw_source_tag == INSTRUMENTATION_SOURCE_TAGS[0]: # 어쿠스틱 설명 태그
        source = 'acoustic'
    else: # 일렉트로닉 설명 태그
        source = 'electronic'

    # 3-1: 감정가
    valence_tag = get_best_tag(audio_embed, text_embeds_dict['valence'], VALENCE_TAGS)
    valence = 'positive' if valence_tag in POSITIVE_SUBGROUP else 'negative'

    # 3-2: 에너지
    energy_tag = get_best_tag(audio_embed, text_embeds_dict['energy'], ENERGY_TAGS)
    if energy_tag in HIGH_ENERGY_SUBGROUP:
        energy = 'high'
    elif energy_tag in LOW_ENERGY_SUBGROUP:
        energy = 'low'
    else:
        energy = 'medium'

    # 4: 세부 분위기
    mood_style = get_best_tag(audio_embed, text_embeds_dict['mood'], MOOD_STYLE_TAGS)

    # 최종 결과 JSON으로 조합
    result = {
        "track_id": track_id,
        "genre": genre,
        "instrumentation": {
            "source": source
        },
        "affect": {
            "valence": valence,
            "energy": energy
        },
        "mood_style": mood_style
    }
    return result

def main():
    print(f"Using device: {DEVICE}")

    # --- 모델 로드 (텍스트 임베딩 계산용) ---
    print("Loading MuQ-MuLan model for text embeddings...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(DEVICE).eval()

    # --- 장르 데이터 로드 ---
    print(f"Loading track and genre data from {TRACKS_CSV_PATH}...")
    try:
        tracks_df = pd.read_csv(TRACKS_CSV_PATH)
        genre_map = pd.Series(tracks_df['top_level_genre_name'].values, index=tracks_df['track_id']).to_dict()
        track_ids = tracks_df['track_id'].tolist()
    except FileNotFoundError:
        print(f"Error: Track CSV file not found at {TRACKS_CSV_PATH}. Aborting.")
        return

    # --- 모든 텍스트 태그 임베딩 미리 계산 ---
    print("Pre-calculating text embeddings for all axes...")
    with torch.no_grad():
        text_embeds_dict = {
            'source': model(texts=INSTRUMENTATION_SOURCE_TAGS).to(DEVICE),
            'valence': model(texts=VALENCE_TAGS).to(DEVICE),
            'energy': model(texts=ENERGY_TAGS).to(DEVICE),
            'mood': model(texts=MOOD_STYLE_TAGS).to(DEVICE)
        }

    # --- 메인 루프: 저장된 임베딩을 읽어와 분석 ---
    print(f"Starting analysis from pre-computed embeddings in {EMBEDDING_DIR}...")
    
    with open(OUTPUT_JSONL_PATH, 'w') as f:
        for track_id in tqdm(track_ids, desc="Analyzing from Embeddings"):
            embedding_path = os.path.join(EMBEDDING_DIR, f"{track_id}.npy")

            if not os.path.exists(embedding_path):
                continue

            # 저장된 임베딩 로드
            embedding_numpy = np.load(embedding_path)
            audio_embed = torch.from_numpy(embedding_numpy).to(DEVICE)
            
            genre = genre_map.get(track_id, 'Unknown')
            
            # 분석 함수 호출
            analysis_result = analyze_embedding(track_id, audio_embed, genre, text_embeds_dict)
            
            if analysis_result:
                f.write(json.dumps(analysis_result) + '\n')

    print("\n--- Analysis from embeddings complete! ---")
    print(f"Results saved to {OUTPUT_JSONL_PATH}")

if __name__ == '__main__':
    main()
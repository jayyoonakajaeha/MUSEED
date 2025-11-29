
import torch
import pandas as pd
import torchaudio
import os
import json
from muq import MuQMuLan
from tqdm import tqdm
import random

# --- 분석을 위한 태그 목록 정의 ---

# 2-1: 악기 음향 소스
INSTRUMENTATION_SOURCE_TAGS = ['acoustic', 'electronic']

# 2-2: 세부 악기 (확장 목록)
SPECIFIC_INSTRUMENT_TAGS = [
    # 현악기 (Strings)
    'violin', 'viola', 'cello', 'contrabass',
    'acoustic guitar', 'electric guitar', 'bass guitar',
    'harp', 'banjo', 'mandolin', 'ukulele',
    # 목관악기 (Woodwinds)
    'flute', 'clarinet', 'oboe', 'bassoon', 'saxophone',
    # 금관악기 (Brass)
    'trumpet', 'trombone', 'french horn', 'tuba',
    # 타악기 (Percussion)
    'drums', 'acoustic drums', 'electronic drums',
    'percussion', 'cymbals', 'tambourine', 'bongo', 'conga',
    'xylophone', 'marimba', 'vibraphone',
    # 건반악기 (Keyboards)
    'piano', 'grand piano', 'electric piano', 'organ', 'harpsichord', 'accordion',
    # 전자악기 (Electronic)
    'synthesizer', 'synth bass', 'synth lead', 'synth pad',
    'drum machine', 'sampler', 'sequencer',
    # 보컬 (Vocals)
    'vocals', 'male vocal', 'female vocal', 'choir', 'backing vocals', 'rap'
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

# 세부 악기 태깅을 위한 유사도 임계값
INSTRUMENT_SIMILARITY_THRESHOLD = 0.7

# 오디오 로딩 함수 (기존 스크립트에서 가져옴)
def load_audio_segment(track_id, audio_dir, sample_rate=16000, duration_samples=160000):
    track_id_str = f"{track_id:06d}"
    file_path = os.path.join(audio_dir, track_id_str[:3], track_id_str + '.mp3')
    try:
        waveform, sr = torchaudio.load(file_path)
        if sr != sample_rate:
            waveform = torchaudio.transforms.Resample(sr, sample_rate)(waveform)
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if waveform.shape[1] < duration_samples:
            waveform = torch.nn.functional.pad(waveform, (0, duration_samples - waveform.shape[1]))
        else:
            start = random.randint(0, waveform.shape[1] - duration_samples)
            waveform = waveform[:, start:start + duration_samples]
        return waveform
    except Exception:
        return None

def get_best_tag(audio_embed, text_embeds, text_labels):
    similarity = torch.nn.functional.cosine_similarity(audio_embed, text_embeds, dim=-1)
    best_tag_index = torch.argmax(similarity).item()
    return text_labels[best_tag_index]

def get_multi_label_tags(audio_embed, text_embeds, text_labels, threshold):
    similarities = torch.nn.functional.cosine_similarity(audio_embed.unsqueeze(0), text_embeds, dim=-1).squeeze(0)
    selected_tags = [text_labels[i] for i, sim in enumerate(similarities) if sim > threshold]
    return selected_tags

def analyze_track(track_id, model, device, audio_dir, genre, text_embeds_dict):
    # 1. 오디오 로드
    waveform = load_audio_segment(track_id, audio_dir)
    if waveform is None:
        return None
    waveform = waveform.to(device)

    # 2. 오디오 임베딩 추출 (한 번만)
    with torch.no_grad():
        audio_embed = model(wavs=waveform)

    # 3. 각 축별로 태그 분석
    # 2-1: 악기 소스
    source = get_best_tag(audio_embed, text_embeds_dict['source'], INSTRUMENTATION_SOURCE_TAGS)
    
    # 2-2: 세부 악기 (Multi-label)
    instruments = get_multi_label_tags(audio_embed, text_embeds_dict['instruments'], SPECIFIC_INSTRUMENT_TAGS, INSTRUMENT_SIMILARITY_THRESHOLD)

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

    # 4. 최종 결과 JSON으로 조합
    result = {
        "track_id": track_id,
        "genre": genre, # 1단계: 데이터 기반 장르
        "instrumentation": {
            "source": source,
            "instruments": instruments
        },
        "affect": {
            "valence": valence,
            "energy": energy
        },
        "mood_style": mood_style
    }
    return result

def main():
    # --- 설정 ---
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tracks_csv_path = '/home/jay/MusicAI/fma/data/fma_metadata/track_toplevel_genres.csv'
    audio_dir = '/home/jay/MusicAI/fma/data/fma_full'
    output_jsonl_path = '/home/jay/MusicAI/multi_axis_analysis_results.jsonl'

    print(f"Using device: {device}")

    # --- 모델 로드 ---
    print("Loading MuQ-MuLan model...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(device).eval()

    # --- 장르 데이터 로드 (1단계) ---
    print(f"Loading track and genre data from {tracks_csv_path}...")
    tracks_df = pd.read_csv(tracks_csv_path)
    # 빠른 조회를 위해 딕셔너리로 변환
    genre_map = pd.Series(tracks_df.genre_toplevel.values, index=tracks_df.track_id).to_dict()
    track_ids = tracks_df['track_id'].tolist()

    # --- 모든 텍스트 태그 임베딩 미리 계산 (최적화) ---
    print("Pre-calculating text embeddings for all axes...")
    with torch.no_grad():
        text_embeds_dict = {
            'source': model(texts=INSTRUMENTATION_SOURCE_TAGS).to(device),
            'instruments': model(texts=SPECIFIC_INSTRUMENT_TAGS).to(device),
            'valence': model(texts=VALENCE_TAGS).to(device),
            'energy': model(texts=ENERGY_TAGS).to(device),
            'mood': model(texts=MOOD_STYLE_TAGS).to(device)
        }

    # --- 메인 루프: 각 트랙 분석 ---
    print(f"Starting multi-axis analysis for {len(track_ids)} tracks...")
    
    with open(output_jsonl_path, 'w') as f:
        for track_id in tqdm(track_ids):
            genre = genre_map.get(track_id, 'Unknown')
            analysis_result = analyze_track(track_id, model, device, audio_dir, genre, text_embeds_dict)
            
            if analysis_result:
                f.write(json.dumps(analysis_result) + '\n')

    print("\n--- Multi-axis analysis complete! ---")
    print(f"Results saved to {output_jsonl_path}")

if __name__ == '__main__':
    main()

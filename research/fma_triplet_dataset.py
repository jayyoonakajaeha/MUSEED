import torch
import pandas as pd
import torchaudio
import random
import os
import json
from torch.utils.data import Dataset, DataLoader

class TripletFmaDataset(Dataset):
    """
    FMA 데이터셋 Triplet 학습용 Dataset 클래스
    (Anchor, Positive, Negative) 쌍 동적 샘플링
    
    핵심 특징: '계층적 샘플링(Hierarchical Sampling)' 구현
    Negative 샘플 격차 보장 위해 태그 계층 구조(장르 -> 분위기 -> 에너지) 활용
    """
    def __init__(self, jsonl_path, audio_dir, sample_rate=16000, duration=10, samples_per_genre=2000):
        """
        Args:
            jsonl_path (str): 메타데이터가 담긴 JSONL 파일 경로
            audio_dir (str): 오디오 파일이 저장된 루트 디렉토리
            sample_rate (int): 오디오 샘플링 레이트 (기본: 16000)
            duration (int): 오디오 클립 길이 (초 단위)
            samples_per_genre (int): 에폭당 장르별로 학습할 샘플 수 (Undersampling & Balancing)
        """
        self.audio_dir = audio_dir
        self.sample_rate = sample_rate
        self.duration_samples = sample_rate * duration
        self.samples_per_genre = samples_per_genre

        print(f"Loading and processing tag data from {jsonl_path}...")
        self.df = self._load_jsonl(jsonl_path)

        # 실제 오디오 파일이 존재하는지 검증하고 필터링합니다.
        self.tracks = self._verify_audio_files()
        self.df = self.df[self.df['track_id'].isin(self.tracks)].reset_index(drop=True)

        if self.df.empty:
            raise RuntimeError("No tracks with existing audio files and tags were found.")

        # --- Balanced Undersampling Setup ---
        # 1. 빠른 조회를 위해 track_id를 인덱스로 하는 DataFrame 별도 생성
        self.df_indexed = self.df.set_index('track_id')

        # 2. 장르별 트랙 리스트 생성
        self.tracks_by_genre = self.df.groupby('genre')['track_id'].apply(list).to_dict()
        self.genres = list(self.tracks_by_genre.keys())
        
        print(f"Dataset initialized. Balanced Undersampling active.")
        print(f"- Genres: {len(self.genres)}")
        print(f"- Samples per genre: {self.samples_per_genre}")
        print(f"- Total samples per epoch: {len(self.genres) * self.samples_per_genre}")

    def _load_jsonl(self, jsonl_path):
        """JSONL 파일에서 트랙 메타데이터 로드 후 DataFrame 변환"""
        records = []
        with open(jsonl_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                records.append({
                    'track_id': data['track_id'],
                    'genre': data['genre'],
                    'source': data['instrumentation']['source'],
                    'valence': data['affect']['valence'],
                    'energy': data['affect']['energy'],
                    'mood_style': data['mood_style']
                })
        return pd.DataFrame(records)

    def _verify_audio_files(self):
        """디렉토리 순회하며 실제 존재 mp3 파일 목록 확인"""
        print(f"Verifying audio files in {self.audio_dir}...")
        return [int(os.path.splitext(f)[0]) for r, d, fs in os.walk(self.audio_dir) for f in fs if f.endswith('.mp3')]

    def __len__(self):
        # 에폭당 전체 샘플 수 = 장르 수 * 장르당 샘플 수
        return len(self.genres) * self.samples_per_genre

    def _load_audio_segment(self, track_id):
        """트랙 ID별 오디오 로드 및 전처리(리샘플링, 모노변환, 자르기/패딩)"""
        track_id_str = f"{track_id:06d}"
        file_path = os.path.join(self.audio_dir, track_id_str[:3], track_id_str + '.mp3')
        try:
            waveform, sr = torchaudio.load(file_path)
            if sr != self.sample_rate:
                waveform = torchaudio.transforms.Resample(sr, self.sample_rate)(waveform)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True) # Stereo -> Mono
            
            # 길이가 짧으면 패딩, 길면 랜덤 구간 추출
            if waveform.shape[1] < self.duration_samples:
                waveform = torch.nn.functional.pad(waveform, (0, self.duration_samples - waveform.shape[1]))
            else:
                start = random.randint(0, waveform.shape[1] - self.duration_samples)
                waveform = waveform[:, start:start + self.duration_samples]
            return waveform
        except Exception as e:
            print(f"Warning: Could not load {file_path}. Error: {e}. Loading random track.")
            # 로드 실패 시 랜덤 트랙으로 대체 (학습 중단 방지)
            random_track_id = random.choice(self.tracks)
            return self._load_audio_segment(random_track_id)

    def __getitem__(self, index):
        """
        학습용 Triplet (Anchor, Positive, Negative) 반환
        """
        # 1. Anchor 선택 (장르 균등 선택)
        # index를 사용하여 장르를 순환 선택함으로써 배치 내 장르 다양성 확보
        genre_idx = index % len(self.genres)
        target_genre = self.genres[genre_idx]
        
        # 해당 장르 내에서 무작위 트랙 선택 (Undersampling 효과)
        anchor_id = random.choice(self.tracks_by_genre[target_genre])
        anchor_row = self.df_indexed.loc[anchor_id] # 빠른 조회

        positive_id = None
        negative_id = None
        positive_level = -1

        # 2. Positive 샘플 찾기 (계층적 검색)
        # Anchor와 최대한 많은 태그 일치 곡을 Positive로 선정
        search_hierarchy = [
            {'genre', 'source', 'valence', 'energy', 'mood_style'}, # Level 0: 모든 태그 일치
            {'genre', 'valence', 'energy', 'mood_style'},          # Level 1
            {'genre', 'valence', 'mood_style'},                   # Level 2
            {'genre', 'mood_style'},                              # Level 3
            {'genre'}                                              # Level 4: 장르만 일치
        ]

        negative_hierarchy = ['source', 'energy', 'mood_style', 'valence', 'genre']

        # Positive 찾기 루프
        for i, tags_to_match in enumerate(search_hierarchy):
            mask = (self.df['track_id'] != anchor_id)
            for tag in tags_to_match:
                mask &= (self.df[tag] == anchor_row[tag])
            
            pool = self.df[mask]
            if not pool.empty:
                positive_id = pool.sample(1)['track_id'].iloc[0]
                positive_level = i
                break

        # Positive를 못 찾은 경우 (희박하지만) Fallback
        if positive_id is None:
            pool = self.df[(self.df['track_id'] != anchor_id) & (self.df['genre'] == anchor_row['genre'])]
            if not pool.empty():
                positive_id = pool.sample(1)['track_id'].iloc[0]
            else:
                positive_id = self.df[self.df['track_id'] != anchor_id].sample(1)['track_id'].iloc[0]
            positive_level = len(search_hierarchy)

        # 3. Negative 샘플 찾기 (Hard Negative Mining)
        # Anchor/Positive 공유 속성보다 더 상위 레벨(더 큰 차이)에서 달라지는 샘플 검색
        # 난이도 순서 (Hard -> Easy): Source 다름 -> Energy 다름 -> Mood 다름 -> Valence 다름 -> Genre 다름
        negative_hierarchy = ['source', 'energy', 'mood_style', 'valence', 'genre']
        
        # 해당 속성이 다르기 위해, 그보다 상위(더 큰 범주)의 속성들은 같아야 "Hard"한 Negative가 됨.
        match_requirements = [
            {'genre', 'valence', 'energy', 'mood_style'}, # Differ in source (나머지 다 같음)
            {'genre', 'valence', 'mood_style'},           # Differ in energy
            {'genre', 'valence'},                         # Differ in mood
            {'genre'},                                    # Differ in valence
            set()                                         # Differ in genre
        ]

        for i in range(positive_level, len(negative_hierarchy)):
            target_diff_tag = negative_hierarchy[i]
            required_matches = match_requirements[i]

            mask = (self.df['track_id'] != anchor_id)
            
            # 1. 필수 일치 조건 (Hardness 확보)
            for tag in required_matches:
                mask &= (self.df[tag] == anchor_row[tag])
            
            # 2. 차별화 조건 (Negative 확보)
            mask &= (self.df[target_diff_tag] != anchor_row[target_diff_tag])

            pool = self.df[mask]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
                break

        # Negative Fallback
        if negative_id is None:
            pool = self.df[self.df['genre'] != anchor_row['genre']]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
            else:
                negative_id = self.df[self.df['track_id'] != anchor_id].sample(1)['track_id'].iloc[0]

        # 4. 오디오 로드 및 반환
        anchor_audio = self._load_audio_segment(anchor_id)
        positive_audio = self._load_audio_segment(positive_id)
        negative_audio = self._load_audio_segment(negative_id)

        return anchor_audio, positive_audio, negative_audio


if __name__ == '__main__':
    # 데이터셋 로더 테스트 코드
    print("--- Testing TripletFmaDataset ---")
    JSONL_PATH = '/home/jay/MusicAI/MUSEED/research/results/train_metadata.jsonl'
    AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'

    if not os.path.exists(JSONL_PATH) or not os.path.exists(AUDIO_DIR):
        print("\nERROR: Prerequisite files not found.")
    else:
        try:
            fma_dataset = TripletFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR)
            # 테스트 속도를 위해 로딩 함수 임시 모킹 (실제 실행 시에는 제거됨)
            # fma_dataset._load_audio_segment = lambda x: torch.zeros(1, 160000)
            anchor, pos, neg = fma_dataset[0]
            print("Successfully sampled one triplet.")
            print(f"Anchor audio shape: {anchor.shape}")
            # 배치 로딩 테스트
            data_loader = DataLoader(fma_dataset, batch_size=2, shuffle=True, num_workers=2)
            next(iter(data_loader))
            print("\n--- DataLoader Test Successful ---")
        except Exception as e:
            print(f"\nAn error occurred during testing: {e}")
            import traceback
            traceback.print_exc()
import os
import json
import random
import torch
import torchaudio
from torch.utils.data import Dataset

class ContrastiveFmaDataset(Dataset):
    def __init__(self, jsonl_path, audio_dir, target_sample_rate=32000, max_duration_sec=10.0, max_samples_per_genre=1500):
        """
        Args:
            jsonl_path (str): 트랙 메타데이터 포함 JSONL 파일 경로
            audio_dir (str): FMA 오디오 파일 루트 디렉토리
            target_sample_rate (int): 모델 기대 샘플 레이트 (MuQ는 32000)
            max_duration_sec (float): 각 오디오 세그먼트 길이
            max_samples_per_genre (int): 불균형 해결 위한 장르당 최대 트랙 수
        """
        self.audio_dir = audio_dir
        self.target_sample_rate = target_sample_rate
        self.max_duration_sec = max_duration_sec
        self.max_samples_per_genre = max_samples_per_genre
        self.num_samples = int(target_sample_rate * max_duration_sec)
        
        self.tracks = []
        self._load_tracks(jsonl_path)

    def _load_tracks(self, jsonl_path):
        """장르 균형 적용하여 JSONL 파일에서 유효 트랙 경로 로드"""
        print(f"Loading tracks from {jsonl_path}...")
        from collections import defaultdict
        genre_tracks = defaultdict(list)

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    track_id = str(data['track_id']).zfill(6)
                    genre = data.get('genre', 'Unknown')
                    
                    # 파일 경로 구성 (예: 000/000123.mp3)
                    rel_path = os.path.join(track_id[:3], f"{track_id}.mp3")
                    full_path = os.path.join(self.audio_dir, rel_path)
                    
                    # 파일 존재 확인
                    if os.path.exists(full_path):
                        genre_tracks[genre].append(full_path)
                except Exception as e:
                    continue
        
        # 장르별 수량 제한 적용
        self.tracks = []
        print("\n--- Genre Distribution (Subset) ---")
        for genre, paths in genre_tracks.items():
            if len(paths) >= self.max_samples_per_genre:
                # 트랙 너무 많으면 언더샘플링
                selected = random.sample(paths, self.max_samples_per_genre)
            else:
                # 트랙 너무 적으면 오버샘플링 (복원 추출)
                selected = random.choices(paths, k=self.max_samples_per_genre)
            
            self.tracks.extend(selected)
            print(f"  {genre}: {len(selected)} tracks (Original: {len(paths)})")
            
        # 배치 내 장르 섞이도록 최종 리스트 셔플
        random.shuffle(self.tracks)
        print(f"\nTotal tracks loaded for training: {len(self.tracks)}")

    def _load_audio(self, path):
        """오디오 로드 및 샘플 레이트/모노 채널 보장"""
        try:
            waveform, sr = torchaudio.load(path)
            
            # 필요 시 리샘플링
            if sr != self.target_sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.target_sample_rate)
                waveform = resampler(waveform)
            
            # 모노 변환 (채널 평균)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            return waveform
        except Exception as e:
            # 실패 시 무음 텐서 반환
            return torch.zeros(1, self.num_samples)

    def _crop_segment(self, waveform):
        """길이 `num_samples` 세그먼트 무작위 크롭"""
        c, t = waveform.shape
        if t <= self.num_samples:
            # 더 짧으면 제로 패딩
            padding = self.num_samples - t
            return torch.nn.functional.pad(waveform, (0, padding))
        else:
            # 무작위 크롭
            start = random.randint(0, t - self.num_samples)
            return waveform[:, start : start + self.num_samples]

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, idx):
        path = self.tracks[idx]
        waveform = self._load_audio(path)
        
        # 동일 트랙에서 서로 다른 두 뷰(세그먼트) 크롭
        # 트랙 충분히 길면 겹치지 않는 게 이상적, But 무작위 크롭이 표준
        segment_a = self._crop_segment(waveform)
        segment_b = self._crop_segment(waveform)
        
        # 정규화
        max_a = segment_a.abs().max()
        if max_a > 1e-6:
            segment_a = segment_a / max_a
            
        max_b = segment_b.abs().max()
        if max_b > 1e-6:
            segment_b = segment_b / max_b

        # Squeeze channel dim: (1, samples) -> (samples,)
        return segment_a.squeeze(0), segment_b.squeeze(0)

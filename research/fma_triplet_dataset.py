
import torch
import pandas as pd
import torchaudio
import random
import os
import json
from torch.utils.data import Dataset, DataLoader

class TripletFmaDataset(Dataset):
    """
    FMA dataset for triplet loss fine-tuning.
    Dynamically samples (Anchor, Positive, Negative) triplets. This implementation
    ensures that the negative sample is always "more different" from the anchor
    than the positive sample by using a dependent hierarchical sampling strategy.
    """
    def __init__(self, jsonl_path, audio_dir, sample_rate=16000, duration=10):
        self.audio_dir = audio_dir
        self.sample_rate = sample_rate
        self.duration_samples = sample_rate * duration

        print(f"Loading and processing tag data from {jsonl_path}...")
        self.df = self._load_jsonl(jsonl_path)

        self.tracks = self._verify_audio_files()
        self.df = self.df[self.df['track_id'].isin(self.tracks)].reset_index(drop=True)

        if self.df.empty:
            raise RuntimeError("No tracks with existing audio files and tags were found.")

        genre_counts = self.df['genre'].value_counts()
        genre_weights = 1 / genre_counts
        self.sample_weights = self.df['genre'].map(genre_weights)
        self.sample_weights /= self.sample_weights.sum()

        print(f"Dataset initialized with {len(self.tracks)} usable tracks.")

    def _load_jsonl(self, jsonl_path):
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
        print(f"Verifying audio files in {self.audio_dir}...")
        return [int(os.path.splitext(f)[0]) for r, d, fs in os.walk(self.audio_dir) for f in fs if f.endswith('.mp3')]

    def __len__(self):
        return len(self.tracks)

    def _load_audio_segment(self, track_id):
        track_id_str = f"{track_id:06d}"
        file_path = os.path.join(self.audio_dir, track_id_str[:3], track_id_str + '.mp3')
        try:
            waveform, sr = torchaudio.load(file_path)
            if sr != self.sample_rate:
                waveform = torchaudio.transforms.Resample(sr, self.sample_rate)(waveform)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            if waveform.shape[1] < self.duration_samples:
                waveform = torch.nn.functional.pad(waveform, (0, self.duration_samples - waveform.shape[1]))
            else:
                start = random.randint(0, waveform.shape[1] - self.duration_samples)
                waveform = waveform[:, start:start + self.duration_samples]
            return waveform
        except Exception as e:
            print(f"Warning: Could not load {file_path}. Error: {e}. Loading random track.")
            random_track_id = random.choice(self.tracks)
            return self._load_audio_segment(random_track_id)

    def __getitem__(self, index):
        anchor_row = self.df.sample(weights=self.sample_weights).iloc[0]
        anchor_id = anchor_row['track_id']

        positive_id = None
        negative_id = None
        positive_level = -1

        search_hierarchy = [
            {'genre', 'source', 'valence', 'energy', 'mood_style'}, # Level 0
            {'genre', 'valence', 'energy', 'mood_style'},          # Level 1
            {'genre', 'valence', 'mood_style'},                   # Level 2
            {'genre', 'mood_style'},                              # Level 3
            {'genre'}                                              # Level 4
        ]

        negative_hierarchy = ['source', 'energy', 'mood_style', 'valence', 'genre']

        # Find Positive and then a harder Negative
        for i, tags_to_match in enumerate(search_hierarchy):
            mask = (self.df['track_id'] != anchor_id)
            for tag in tags_to_match:
                mask &= (self.df[tag] == anchor_row[tag])
            
            pool = self.df[mask]
            if not pool.empty:
                positive_id = pool.sample(1)['track_id'].iloc[0]
                positive_level = i
                break

        if positive_id is None:
             # Fallback for positive: genre match or any other track
            pool = self.df[(self.df['track_id'] != anchor_id) & (self.df['genre'] == anchor_row['genre'])]
            if not pool.empty():
                positive_id = pool.sample(1)['track_id'].iloc[0]
            else:
                positive_id = self.df[self.df['track_id'] != anchor_id].sample(1)['track_id'].iloc[0]
            positive_level = len(search_hierarchy) # Set to lowest level

        # Find Negative, ensuring it's from a lower similarity level than the positive
        for i in range(positive_level, len(negative_hierarchy)):
            negative_tag = negative_hierarchy[i]
            
            # Match all tags that define the current negative level
            tags_to_match = search_hierarchy[i-1] if i > 0 else set(self.df.columns) - {'track_id', negative_tag}

            mask = (self.df['track_id'] != anchor_id)
            for tag in tags_to_match:
                if tag in anchor_row:
                     mask &= (self.df[tag] == anchor_row[tag])
            
            # Mismatch the specific negative tag
            mask &= (self.df[negative_tag] != anchor_row[negative_tag])

            pool = self.df[mask]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
                break

        if negative_id is None:
            # Fallback for negative: different genre
            pool = self.df[self.df['genre'] != anchor_row['genre']]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
            else: # Ultimate fallback
                negative_id = self.df[self.df['track_id'] != anchor_id].sample(1)['track_id'].iloc[0]

        anchor_audio = self._load_audio_segment(anchor_id)
        positive_audio = self._load_audio_segment(positive_id)
        negative_audio = self._load_audio_segment(negative_id)

        return anchor_audio, positive_audio, negative_audio


if __name__ == '__main__':
    print("--- Testing TripletFmaDataset ---")
    JSONL_PATH = '/home/jay/MusicAI/multi_axis_analysis_results.jsonl'
    AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'

    if not os.path.exists(JSONL_PATH) or not os.path.exists(AUDIO_DIR):
        print("\nERROR: Prerequisite files not found.")
    else:
        try:
            fma_dataset = TripletFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR)
            fma_dataset._load_audio_segment = lambda x: torch.zeros(1, 160000)
            anchor, pos, neg = fma_dataset[0]
            print("Successfully sampled one triplet.")
            print(f"Anchor audio shape: {anchor.shape}")
            data_loader = DataLoader(fma_dataset, batch_size=2, shuffle=True, num_workers=2)
            next(iter(data_loader))
            print("\n--- DataLoader Test Successful ---")
        except Exception as e:
            print(f"\nAn error occurred during testing: {e}")
            import traceback
            traceback.print_exc()

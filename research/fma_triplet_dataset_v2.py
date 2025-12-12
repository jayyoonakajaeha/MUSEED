import torch
import pandas as pd
import torchaudio
import random
import os
import json
from torch.utils.data import Dataset, DataLoader

class TripletFmaDatasetV2(Dataset):
    """
    FMA Dataset for Triplet Learning V2 (Stochastic Hard Negative Mining).
    
    unlike V1 (Hierarchical), this V2 dataset treats all 5 attributes with EQUAL priority.
    For each sample, it randomly selects one attribute (e.g., 'energy') to be the 'differentiating factor'
    and strictly requires ALL other attributes to match.
    """
    def __init__(self, jsonl_path, audio_dir, sample_rate=16000, duration=10, samples_per_genre=500):
        self.audio_dir = audio_dir
        self.sample_rate = sample_rate
        self.duration_samples = sample_rate * duration
        self.samples_per_genre = samples_per_genre

        print(f"[V2 Dataset] Loading tags from {jsonl_path}...")
        self.df = self._load_jsonl(jsonl_path)

        self.tracks = self._verify_audio_files()
        self.df = self.df[self.df['track_id'].isin(self.tracks)].reset_index(drop=True)

        if self.df.empty:
            raise RuntimeError("No tracks found.")

        # Indexing for speed
        self.df_indexed = self.df.set_index('track_id')
        self.tracks_by_genre = self.df.groupby('genre')['track_id'].apply(list).to_dict()
        self.genres = list(self.tracks_by_genre.keys())
        
        print(f"[V2 Dataset] Initialized with Stochastic Hard Mining.")
        print(f"- Genres: {len(self.genres)}")
        print(f"- Samples per genre: {self.samples_per_genre}")

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
        return [int(os.path.splitext(f)[0]) for r, d, fs in os.walk(self.audio_dir) for f in fs if f.endswith('.mp3')]

    def __len__(self):
        return len(self.genres) * self.samples_per_genre

    def _load_audio_segment(self, track_id):
        # Implementation identical to V1
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
        except Exception:
            return torch.zeros(1, self.duration_samples) 

    def __getitem__(self, index):
        # 1. Anchor
        genre_idx = index % len(self.genres)
        target_genre = self.genres[genre_idx]
        anchor_id = random.choice(self.tracks_by_genre[target_genre])
        anchor_row = self.df_indexed.loc[anchor_id]

        # 2. Positive (Same logic as V1 or simplified to "Max Match")
        # For V2, let's try to find a "Perfect Match" first
        positive_id = None
        
        # Priority 1: Match Everything
        # Priority 2: Match Genre + (Mood/Energy/Valence)
        # Priority 3: Match Genre
        positive_strategies = [
            {'genre', 'source', 'valence', 'energy', 'mood_style'},
            {'genre', 'valence', 'energy', 'mood_style'},
            {'genre'}
        ]
        
        for tags in positive_strategies:
            mask = (self.df['track_id'] != anchor_id)
            for tag in tags:
                mask &= (self.df[tag] == anchor_row[tag])
            
            pool = self.df[mask]
            if not pool.empty:
                positive_id = pool.sample(1)['track_id'].iloc[0]
                break
        
        if positive_id is None:
             # Just random same genre
             pool = self.df[(self.df['track_id'] != anchor_id) & (self.df['genre'] == anchor_row['genre'])]
             if not pool.empty:
                 positive_id = pool.sample(1)['track_id'].iloc[0]
             else:
                 # Should not happen considering dataset size
                 positive_id = anchor_id 

        # 3. Negative (Stochastic Hard Mining)
        negative_id = None
        
        # Define 4 types of "Strict Hard Negatives"
        # Each strategy aims to find a track that differs ONLY in the target_diff_tag
        # but matches in ALL other tags.
        all_tags = {'source', 'energy', 'mood_style', 'valence', 'genre'}
        
        strategies = [
            'source', 
            'energy', 
            'mood_style', 
            'valence'
            # Note: 'genre' is the Easy Negative fallback
        ]
        
        # Shuffle strategies to give equal priority
        random.shuffle(strategies)
        
        for target_diff_tag in strategies:
            # required_matches = all tags EXCEPT target_diff_tag
            required_matches = all_tags - {target_diff_tag}
            
            mask = (self.df['track_id'] != anchor_id)
            
            # Constraint 1: Must match all other attributes
            for tag in required_matches:
                mask &= (self.df[tag] == anchor_row[tag])
            
            # Constraint 2: Must differ in the target attribute
            mask &= (self.df[target_diff_tag] != anchor_row[target_diff_tag])
            
            pool = self.df[mask]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
                # print(f"Found Hard Negative type: {target_diff_tag}")
                break
        
        # Fallback: Easy Negative (Different Genre)
        if negative_id is None:
            pool = self.df[self.df['genre'] != anchor_row['genre']]
            if not pool.empty:
                negative_id = pool.sample(1)['track_id'].iloc[0]
            else:
                 negative_id = anchor_id

        anchor_audio = self._load_audio_segment(anchor_id)
        positive_audio = self._load_audio_segment(positive_id)
        negative_audio = self._load_audio_segment(negative_id)

        return anchor_audio, positive_audio, negative_audio

import os
import json
import random
import torch
import torchaudio
from torch.utils.data import Dataset

class ContrastiveFmaDataset(Dataset):
    def __init__(self, jsonl_path, audio_dir, target_sample_rate=32000, max_duration_sec=10.0):
        """
        Args:
            jsonl_path (str): Path to the JSONL file containing track metadata.
            audio_dir (str): Root directory of the FMA audio files.
            target_sample_rate (int): Sample rate expected by the model (MuQ expects 32000).
            max_duration_sec (float): Duration of each audio segment.
        """
        self.audio_dir = audio_dir
        self.target_sample_rate = target_sample_rate
        self.max_duration_sec = max_duration_sec
        self.num_samples = int(target_sample_rate * max_duration_sec)
        
        self.tracks = []
        self._load_tracks(jsonl_path)

    def _load_tracks(self, jsonl_path):
        """Loads valid track paths from the JSONL file."""
        print(f"Loading tracks from {jsonl_path}...")
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    track_id = str(data['track_id']).zfill(6)
                    # Construct file path (e.g., 000/000123.mp3)
                    rel_path = os.path.join(track_id[:3], f"{track_id}.mp3")
                    full_path = os.path.join(self.audio_dir, rel_path)
                    
                    # Verify file existence
                    if os.path.exists(full_path):
                        self.tracks.append(full_path)
                except Exception as e:
                    continue
        print(f"Loaded {len(self.tracks)} valid tracks.")

    def _load_audio(self, path):
        """Loads audio and ensures correct sample rate and mono channel."""
        try:
            waveform, sr = torchaudio.load(path)
            
            # Resample if necessary
            if sr != self.target_sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.target_sample_rate)
                waveform = resampler(waveform)
            
            # Convert to mono (average channels)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            return waveform
        except Exception as e:
            # Return silent tensor on failure
            return torch.zeros(1, self.num_samples)

    def _crop_segment(self, waveform):
        """Randomly crops a segment of length `num_samples`."""
        c, t = waveform.shape
        if t <= self.num_samples:
            # If shorter, pad with zeros
            padding = self.num_samples - t
            return torch.nn.functional.pad(waveform, (0, padding))
        else:
            # Random crop
            start = random.randint(0, t - self.num_samples)
            return waveform[:, start : start + self.num_samples]

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, idx):
        path = self.tracks[idx]
        waveform = self._load_audio(path)
        
        # Crop two different views (segments) from the same track
        # Ideally, these should be non-overlapping if the track is long enough, 
        # but random crop is standard practice.
        segment_a = self._crop_segment(waveform)
        segment_b = self._crop_segment(waveform)
        
        # Normalize
        max_a = segment_a.abs().max()
        if max_a > 1e-6:
            segment_a = segment_a / max_a
            
        max_b = segment_b.abs().max()
        if max_b > 1e-6:
            segment_b = segment_b / max_b

        # Squeeze channel dim: (1, samples) -> (samples,)
        return segment_a.squeeze(0), segment_b.squeeze(0)

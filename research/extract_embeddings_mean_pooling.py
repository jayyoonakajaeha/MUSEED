
import torch
import torchaudio
import os
import json
import numpy as np
from tqdm import tqdm
import math
import argparse
from muq import MuQ

# --- Configuration ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
SAMPLE_RATE = 32000 # Correct SR for Contrastive V2 model
DURATION_SAMPLES = SAMPLE_RATE * 10 # 10 seconds

def load_audio_segments(file_path):
    """
    Loads Start, Center, and End segments (10s each).
    Returns: Tensor of shape (3, 1, DURATION_SAMPLES) or fewer if short.
             If file < 10s, returns (1, 1, DURATION_SAMPLES) padded.
    """
    if not os.path.exists(file_path):
        return None

    try:
        # Load audio
        waveform, sr = torchaudio.load(file_path)
        
        # Resample
        if sr != SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(sr, SAMPLE_RATE)
            waveform = resampler(waveform)
        
        # Mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            
        total_samples = waveform.shape[1]
        
        # Case 1: Less than 10s -> Pad and return single
        if total_samples < DURATION_SAMPLES:
            padding = DURATION_SAMPLES - total_samples
            waveform = torch.nn.functional.pad(waveform, (0, padding))
            return waveform.unsqueeze(0) # (1, 1, 320000)

        segments = []
        
        # 1. 시작 (0 ~ 10초)
        start_segment = waveform[:, :DURATION_SAMPLES]
        segments.append(start_segment)
        
        # 2. 중간
        center_start = (total_samples - DURATION_SAMPLES) // 2
        center_segment = waveform[:, center_start : center_start + DURATION_SAMPLES]
        segments.append(center_segment)
        
        # 3. 끝 (마지막 10초)
        end_segment = waveform[:, -DURATION_SAMPLES:]
        segments.append(end_segment)
        
        return torch.stack(segments) # (3, 1, 320000)

    except Exception as e:
        # print(f"Warning: Could not load {file_path}: {e}")
        return None

def main(args):
    print(f"Using device: {DEVICE}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Model Path: {args.model_path}")
    
    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Load Model
    print("Loading MuQ Base Architecture...")
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
    
    print(f"Loading Fine-tuned weights from {args.model_path}...")
    try:
        state_dict = torch.load(args.model_path, map_location=DEVICE)
        model.load_state_dict(state_dict)
    except Exception as e:
        print(f"Error loading weights: {e}")
        return
            
    model.to(DEVICE).eval()
    print("Model loaded successfully.")

    # 2. Load Metadata
    tracks = []
    print(f"Loading tracks from JSONL: {args.input_path}...")
    with open(args.input_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                tracks.append(data['track_id'])
            except:
                pass

    print(f"Found {len(tracks)} tracks in metadata.")
    
    # Check already processed
    processed_files = set(os.listdir(args.output_dir))
    
    # 3. Processing
    count = 0
    batch_size = args.batch_size # Number of tracks to process at once? No, inference is usually 1 track (3 segments) -> Batch 3
    
    # We process one track at a time, but batch the 3 segments
    
    for track_id in tqdm(tracks, desc="Extracting Embeddings"):
        filename = f"{track_id}.npy"
        if filename in processed_files and not args.overwrite:
            continue
            
        track_id_str = f"{track_id:06d}"
        fma_path = os.path.join(args.audio_dir, track_id_str[:3], track_id_str + '.mp3')
        
        if not os.path.exists(fma_path):
             continue

        # Get 3 segments
        segments_tensor = load_audio_segments(fma_path) # (3, 1, 320000)
        if segments_tensor is None:
            continue
            
        try:
            with torch.no_grad():
                # 배치 전달 (3, 1, 320000)
                batch = segments_tensor.to(DEVICE)
                
                # 순전파
                # MuQ 출력: output.last_hidden_state
                output = model(batch)
                
                # CLS 토큰 임베딩 추출 (인덱스 0)
                # shape: (3, seq_len, 1024) -> (3, 1024)
                embeddings = output.last_hidden_state[:, 0, :]
                
                # 3개 세그먼트에 대한 평균 풀링
                # shape: (1024,)
                final_embedding = torch.mean(embeddings, dim=0)
                
                # 정규화 (선택사항, 코사인 유사도에 유리)
                # final_embedding = torch.nn.functional.normalize(final_embedding, p=2, dim=0)
                
                np.save(os.path.join(args.output_dir, filename), final_embedding.cpu().numpy())
                count += 1
                
        except Exception as e:
            print(f"Error processing {track_id}: {e}")

    print(f"Done. Processed {count} tracks.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--input_path', type=str, required=True)
    parser.add_argument('--audio_dir', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--batch_size', type=int, default=1) # Not really used, processing 1 track (3 segs) at a time
    parser.add_argument('--overwrite', action='store_true')
    
    args = parser.parse_args()
    main(args)


import torch
import torchaudio
import os
import json
import numpy as np
from tqdm import tqdm
import math
import argparse
from muq import MuQ, MuQMuLan

# --- Configuration defaults ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
SAMPLE_RATE = 16000

def load_audio_windows(file_path, window_seconds=10, stride_seconds=10):
    """
    전체 오디오 로드 및 슬라이딩 윈도우 추출
    Returns: Tensor (윈도우 수, 1, 윈도우 샘플 수)
    """
    window_samples = SAMPLE_RATE * window_seconds
    stride_samples = SAMPLE_RATE * stride_seconds
    
    if not os.path.exists(file_path):
        return None

    try:
        # Load full audio
        waveform, sr = torchaudio.load(file_path)
        if sr != SAMPLE_RATE:
            waveform = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(waveform)
        
        # Convert to mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True) # (1, Total_Samples)
            
        total_samples = waveform.shape[1]
        
        # 윈도우보다 짧을 경우 패딩
        if total_samples < window_samples:
            padding = window_samples - total_samples
            waveform = torch.nn.functional.pad(waveform, (0, padding))
            return waveform.unsqueeze(0) # (1, 1, window_samples)

        # 슬라이딩 윈도우 추출
        windows = []
        num_windows = math.ceil((total_samples - window_samples) / stride_samples) + 1
        
        for i in range(num_windows):
            start = i * stride_samples
            end = start + window_samples
            
            if end <= total_samples:
                window = waveform[:, start:end]
            else:
                # 마지막 윈도우: 패딩 아티팩트 방지를 위해 뒤에서부터 정확히 자름
                window = waveform[:, -window_samples:]
                
            windows.append(window)
            
        if not windows:
            return None
            
        return torch.stack(windows) # (N, 1, window_samples)

    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return None

def main(args):
    print(f"Using device: {DEVICE}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Window Strategy: {args.window_size}s Window, {args.stride}s Stride")
    
    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Load Model
    if args.model_type == 'muq':
        print("Loading MuQ Base Architecture...")
        model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
        if args.model_path and args.model_path != 'base':
            print(f"Loading Fine-tuned weights from {args.model_path}...")
            state_dict = torch.load(args.model_path, map_location=DEVICE)
            model.load_state_dict(state_dict)
            
    elif args.model_type == 'mulan':
        print("Loading MuQ-MuLan Architecture (Teacher)...")
        model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large")
    
    model.to(DEVICE).eval()
    print("Model loaded successfully.")

    # 2. Load Track List
    tracks = []
    # Support both JSONL (metadata) and CSV (raw list) or Directory walk?
    # Let's support JSONL as primary, or direct ID list.
    if args.input_path.endswith('.jsonl'):
        print(f"Loading tracks from JSONL: {args.input_path}...")
        with open(args.input_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    tracks.append(data['track_id'])
                except:
                    pass
    else:
        # Fallback: Is it a directory?
        print("Input path not JSONL, feature not fully implemented for directory walk yet.")
        return

    print(f"Found {len(tracks)} tracks to process.")

    # 3. Processing
    count = 0
    
    for track_id in tqdm(tracks, desc="Extracting Embeddings"):
        output_path = os.path.join(args.output_dir, f"{track_id}.npy")
        
        if os.path.exists(output_path) and not args.overwrite:
            continue
            
        # Construct Audio Path (Assume FMA structure or flat?)
        # Logic: If audio_dir has subfolders '000', '001'... use FMA logic.
        track_id_str = f"{track_id:06d}"
        fma_path = os.path.join(args.audio_dir, track_id_str[:3], track_id_str + '.mp3')
        
        if os.path.exists(fma_path):
            file_path = fma_path
        else:
             # Try flat structure
             flat_path = os.path.join(args.audio_dir, track_id_str + '.mp3')
             if os.path.exists(flat_path):
                 file_path = flat_path
             else:
                 # Try with filename from metadata if available? For now stick to ID.
                 continue

        # Get batch of windows
        windows_batch = load_audio_windows(file_path, args.window_size, args.stride)
        if windows_batch is None:
            continue
            
            # 미니배치 처리
            try:
                with torch.no_grad():
                    for i in range(0, total_windows, args.batch_size):
                        batch = windows_batch[i : i + args.batch_size].to(DEVICE)
                        
                        # 순전파
                        output = model(batch, output_hidden_states=False)
                        # 시간축 평균 -> (B, 768)
                        batch_embeddings = output.last_hidden_state.mean(dim=1)
                        embeddings_list.append(batch_embeddings.cpu())
                        
                # 모든 윈도우 임베딩 연결
                full_embeddings = torch.cat(embeddings_list, dim=0) # (N, 768)
                
                # 최종 집계 (모든 윈도우 평균 풀링)
                final_embedding = full_embeddings.mean(dim=0) # (768,)
            
            np.save(output_path, final_embedding.numpy())
            count += 1
            
        except Exception as e:
            print(f"Error processing {track_id}: {e}")

    print(f"Done. Processed {count} tracks.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract Audio Embeddings using MuQ/MuLan')
    parser.add_argument('--model_path', type=str, default='base', help='Path to .pth checkpoint or "base"')
    parser.add_argument('--model_type', type=str, default='muq', choices=['muq', 'mulan'], help='Model Architecture')
    parser.add_argument('--input_path', type=str, required=True, help='Path to metadata.jsonl input')
    parser.add_argument('--audio_dir', type=str, required=True, help='Root directory of audio files')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for .npy files')
    parser.add_argument('--window_size', type=int, default=10, help='Window size in seconds')
    parser.add_argument('--stride', type=int, default=10, help='Stride in seconds (Default 10 = No Overlap)')
    parser.add_argument('--batch_size', type=int, default=32, help='Inference batch size')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing embeddings')
    
    args = parser.parse_args()
    main(args)

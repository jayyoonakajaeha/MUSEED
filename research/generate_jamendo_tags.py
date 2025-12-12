import torch
import os
import json
import numpy as np
from muq import MuQMuLan
from tqdm import tqdm

# --- Tags Definition (Same as analyze_from_embeddings.py) ---
INSTRUMENTATION_SOURCE_TAGS = [
    'acoustic sound, natural instruments, unplugged, raw, organic, live recording',
    'electronic sound, synthesized, processed, digital instruments, programmed beats, effects, modulated'
]
VALENCE_TAGS = ['positive', 'bright', 'happy', 'cheerful', 'negative', 'dark', 'sad', 'angry']
POSITIVE_SUBGROUP = ['positive', 'bright', 'happy', 'cheerful']
ENERGY_TAGS = ['high energy', 'energetic', 'intense', 'medium energy', 'moderate', 'low energy', 'calm', 'relaxed', 'peaceful']
HIGH_ENERGY_SUBGROUP = ['high energy', 'energetic', 'intense']
LOW_ENERGY_SUBGROUP = ['low energy', 'calm', 'relaxed', 'peaceful']
MOOD_STYLE_TAGS = ['funky', 'groovy', 'sentimental', 'romantic', 'epic', 'cinematic', 'powerful', 'ambient', 'experimental', 'minimalist', 'strange', 'dark']

# --- Config ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
JAMENDO_METADATA_PATH = '/home/jay/MusicAI/jamendo_formatted/jamendo_metadata.jsonl'
EMBEDDING_DIR = '/home/jay/MusicAI/jamendo_embeddings_mulan/' # Corrected path
OUTPUT_JSONL_PATH = '/home/jay/MusicAI/MUSEED/data/jamendo_rich_metadata.jsonl'

def get_best_tag(audio_embed, text_embeds, text_labels):
    similarity = torch.nn.functional.cosine_similarity(audio_embed, text_embeds, dim=-1)
    best_tag_index = torch.argmax(similarity).item()
    return text_labels[best_tag_index]

def analyze_embedding(track_id, audio_embed, genre, text_embeds_dict):
    # 2: Instrumentation Source
    raw_source_tag = get_best_tag(audio_embed, text_embeds_dict['source'], INSTRUMENTATION_SOURCE_TAGS)
    if raw_source_tag == INSTRUMENTATION_SOURCE_TAGS[0]:
        source = 'acoustic'
    else:
        source = 'electronic'

    # 3-1: Valence
    valence_tag = get_best_tag(audio_embed, text_embeds_dict['valence'], VALENCE_TAGS)
    valence = 'positive' if valence_tag in POSITIVE_SUBGROUP else 'negative'

    # 3-2: Energy
    energy_tag = get_best_tag(audio_embed, text_embeds_dict['energy'], ENERGY_TAGS)
    if energy_tag in HIGH_ENERGY_SUBGROUP:
        energy = 'high'
    elif energy_tag in LOW_ENERGY_SUBGROUP:
        energy = 'low'
    else:
        energy = 'medium'

    # 4: Mood
    mood_style = get_best_tag(audio_embed, text_embeds_dict['mood'], MOOD_STYLE_TAGS)

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

# --- Audio Processing ---
import torchaudio
import torchaudio.transforms as T

def load_audio(path, target_sr=24000):
    try:
        waveform, sr = torchaudio.load(path)
        if sr != target_sr:
            resampler = T.Resample(sr, target_sr)
            waveform = resampler(waveform)
        # MuQMuLan expects (1, samples) or (B, samples)
        # Ensure mono if needed? Model handles stereo usually, but let's check input requirements.
        # Assuming model handles (C, T) or (B, C, T) or (B, T).
        # evaluate_model.py squeezed (B, 1, T) to (B, T).
        # Let's keep it as (1, samples) for single item batch.
        return waveform
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def main():
    print(f"Using device: {DEVICE}")
    AUDIO_DIR = '/home/jay/MusicAI/jamendo_formatted/data'

    # 1. Load Track IDs and basic Genre from Jamendo Metadata
    print(f"Loading Jamendo metadata from {JAMENDO_METADATA_PATH}...")
    track_genre_map = {}
    if os.path.exists(JAMENDO_METADATA_PATH):
        with open(JAMENDO_METADATA_PATH, 'r') as f:
            for line in f:
                item = json.loads(line)
                track_genre_map[item['track_id']] = item.get('genre', 'Unknown')
    else:
        print(f"Error: Metadata file not found at {JAMENDO_METADATA_PATH}")
        return

    track_ids = list(track_genre_map.keys())
    print(f"Loaded {len(track_ids)} tracks.")

    # 2. Load MuQ-MuLan for Text Embeddings AND Audio processing
    print("Loading MuQ-MuLan model...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(DEVICE).eval()

    # 3. Pre-calculate text embeddings
    print("Pre-calculating text embeddings...")
    with torch.no_grad():
        text_embeds_dict = {
            'source': model(texts=INSTRUMENTATION_SOURCE_TAGS).to(DEVICE),
            'valence': model(texts=VALENCE_TAGS).to(DEVICE),
            'energy': model(texts=ENERGY_TAGS).to(DEVICE),
            'mood': model(texts=MOOD_STYLE_TAGS).to(DEVICE)
        }

    # 4. Analyze Audio Directly
    print("Starting analysis (Audio -> Embedding -> Tags)...")
    processed_count = 0
    with open(OUTPUT_JSONL_PATH, 'w') as f:
        for track_id in tqdm(track_ids, desc="Generating Tags"):
            if str(track_id) == '900007': # Skip corrupt file
                 continue

            track_id_str = str(track_id).zfill(6)
            subdir = track_id_str[:3]
            audio_path = os.path.join(AUDIO_DIR, subdir, f"{track_id_str}.mp3")
            
            if not os.path.exists(audio_path):
                print(f"Audio not found: {audio_path}")
                continue

            waveform = load_audio(audio_path)
            if waveform is None:
                continue
            
            # Prepare batch of size 1
            waveform = waveform.to(DEVICE)
            # MuQMuLan expects (B, T) usually if input is 'wavs'
            # waveform is (C, T). If stereo, (2, T). If mono (1, T).
            # Model usually handles (B, T) -> treats as mono?
            # Safe bet: mix to mono if stereo, then unsqueeze to (1, T)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # waveform is (1, T). Call model(wavs=waveform)
            # Model call: wavs: torch.Tensor of shape (batch, samples).
            # So pass (1, T) is correct? No, (batch, samples) means 2D.
            # waveform (1, T) is 2D. So it's treated as batch=1, samples=T. Correct.
            
            try:
                with torch.no_grad():
                    audio_embed = model(wavs=waveform)
                    # audio_embed: (1, D)
                
                genre = track_genre_map[track_id]
                result = analyze_embedding(track_id, audio_embed, genre, text_embeds_dict)
                f.write(json.dumps(result) + '\n')
                processed_count += 1
            except Exception as e:
                print(f"Error processing {track_id}: {e}")
                continue

    print(f"\n--- Analysis complete! {processed_count}/{len(track_ids)} tracks processed. ---")
    print(f"Rich metadata saved to {OUTPUT_JSONL_PATH}")

if __name__ == '__main__':
    main()

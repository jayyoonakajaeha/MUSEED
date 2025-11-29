
import torch
import numpy as np
from muq import MuQMuLan

# --- 설정 ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TRACK_ID = 26532
EMBEDDING_PATH = f"/home/jay/MusicAI/fma_audio_embeddings/{TRACK_ID}.npy"
INSTRUMENTATION_SOURCE_TAGS = ['acoustic', 'electronic']

def debug_source_similarity():
    print(f"--- Debugging source tag for track_id: {TRACK_ID} ---")
    print(f"Using device: {DEVICE}")

    # --- 모델 로드 ---
    print("Loading MuQ-MuLan model...")
    model = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large").to(DEVICE).eval()

    # --- 오디오 임베딩 로드 ---
    try:
        print(f"Loading audio embedding from {EMBEDDING_PATH}...")
        embedding_numpy = np.load(EMBEDDING_PATH)
        audio_embed = torch.from_numpy(embedding_numpy).to(DEVICE)
    except FileNotFoundError:
        print(f"Error: Embedding file not found at {EMBEDDING_PATH}. Aborting.")
        return

    # --- 텍스트 태그 임베딩 계산 ---
    print(f"Calculating text embeddings for: {INSTRUMENTATION_SOURCE_TAGS}")
    with torch.no_grad():
        text_embeds = model(texts=INSTRUMENTATION_SOURCE_TAGS).to(DEVICE)

    # --- 유사도 계산 ---
    similarities = torch.nn.functional.cosine_similarity(audio_embed.unsqueeze(0), text_embeds, dim=-1).squeeze(0)

    # --- 결과 출력 ---
    print("\n--- Cosine Similarity Scores ---")
    for i, tag in enumerate(INSTRUMENTATION_SOURCE_TAGS):
        print(f"'{tag}': {similarities[i].item():.4f}")

    best_tag_index = torch.argmax(similarities).item()
    best_tag = INSTRUMENTATION_SOURCE_TAGS[best_tag_index]
    print(f"\nModel chose: '{best_tag}' (Highest similarity)")
    print("------------------------------------")

if __name__ == '__main__':
    debug_source_similarity()

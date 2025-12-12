import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import os
from datetime import datetime

from fma_triplet_dataset_v2 import TripletFmaDatasetV2
from muq import MuQ

# --- 설정 (Configuration) ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# 경로 설정
JSONL_PATH = '/home/jay/MusicAI/MUSEED/data/train_metadata.jsonl'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
MODEL_SAVE_DIR = '/home/jay/MusicAI/MUSEED/models/'

# 베이스 모델: Contrastive Learning(SimCLR)으로 학습된 모델 사용
BASE_MODEL_PATH = '/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v2.pth'

# 저장될 모델 이름: Hybrid (Contrastive + Triplet)
MODEL_NAME = "muq_hybrid_v1.pth"
LOG_DIR = "runs/muq_hybrid_v1"

# 하이퍼파라미터
LEARNING_RATE = 1e-5  
BATCH_SIZE = 16      
NUM_EPOCHS = 5        
MARGIN = 0.20         
NUM_WORKERS = 4       

# 중요: 학습 속도를 위해 장르당 샘플 수를 500으로 제한
SAMPLES_PER_GENRE = 500 

def train():
    """
    MuQ Hybrid Fine-tuning (Contrastive -> Triplet)
    """
    print(f"Using device: {DEVICE}")
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_log_dir = os.path.join(LOG_DIR, timestamp)
    print(f"TensorBoard logs will be saved to: {unique_log_dir}")
    writer = SummaryWriter(unique_log_dir)

    # 1. 모델 로드 (Load Model)
    print(f"Loading base MuQ model and loading weights from {BASE_MODEL_PATH}...")
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)
    
    # Contrastive 학습된 가중치 로드
    if os.path.exists(BASE_MODEL_PATH):
        try:
            state_dict = torch.load(BASE_MODEL_PATH, map_location=DEVICE)
            model.load_state_dict(state_dict)
            print("Successfully loaded Contrastive V2 weights.")
        except Exception as e:
            print(f"Error loading weights: {e}")
            return
    else:
        print(f"Error: Base model file not found at {BASE_MODEL_PATH}")
        return

    # --- 부분 파인튜닝 (Partial Fine-tuning) 설정 ---
    print("\n--- Setting up partial fine-tuning ---")
    for param in model.parameters():
        param.requires_grad = False
    
    # Conformer 6~11번 레이어 및 Linear 헤드 학습
    for i in range(6, 12):
        for param in model.model.conformer.layers[i].parameters():
            param.requires_grad = True
    for param in model.model.linear.parameters():
        param.requires_grad = True

    params_to_update = [p for p in model.parameters() if p.requires_grad]
    print(f"Training {len(params_to_update)} parameter tensors.")

    # 2. 데이터셋 및 데이터로더 초기화
    print(f"Initializing TripletFmaDataset with {SAMPLES_PER_GENRE} samples per genre...")
    try:
        dataset = TripletFmaDatasetV2(
            jsonl_path=JSONL_PATH, 
            audio_dir=AUDIO_DIR, 
            samples_per_genre=SAMPLES_PER_GENRE # 500으로 제한
        )
        dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    except Exception as e:
        print(f"Error initializing dataset: {e}")
        writer.close()
        return

    # 3. 학습 준비
    optimizer = AdamW(params_to_update, lr=LEARNING_RATE)
    triplet_loss_fn = nn.TripletMarginLoss(margin=MARGIN, p=2)

    print(f"\n--- Starting Hybrid Training: Target '{MODEL_NAME}' ---")
    model.train()

    try:
        global_step = 0
        for epoch in range(NUM_EPOCHS):
            total_loss = 0.0
            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}")

            for anchor_audio, positive_audio, negative_audio in progress_bar:
                anchor_audio = anchor_audio.to(DEVICE)
                positive_audio = positive_audio.to(DEVICE)
                negative_audio = negative_audio.to(DEVICE)

                optimizer.zero_grad()

                # CLS 토큰 임베딩 사용
                anchor_embed = model(anchor_audio).last_hidden_state[:, 0, :]
                positive_embed = model(positive_audio).last_hidden_state[:, 0, :]
                negative_embed = model(negative_audio).last_hidden_state[:, 0, :]
                
                loss = triplet_loss_fn(anchor_embed, positive_embed, negative_embed)

                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})

                writer.add_scalar('Loss/step', loss.item(), global_step)
                global_step += 1

            avg_loss = total_loss / len(dataloader)
            print(f"\nEnd of Epoch {epoch + 1}, Average Loss: {avg_loss:.4f}")
            writer.add_scalar('Loss/epoch', avg_loss, epoch)

    except KeyboardInterrupt:
        print("\n--- Training interrupted by user. Saving current model state... ---")
        save_path = os.path.join(MODEL_SAVE_DIR, f"interrupted_{MODEL_NAME}")
        torch.save(model.state_dict(), save_path)
        print(f"Model saved to {save_path}")
        writer.close()
        return

    print("\n--- Training Finished ---")
    save_path = os.path.join(MODEL_SAVE_DIR, MODEL_NAME)
    torch.save(model.state_dict(), save_path)
    print(f"Hybrid fine-tuned model saved to {save_path}")
    
    writer.close()

if __name__ == '__main__':
    train()

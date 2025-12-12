import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import os
from datetime import datetime

from fma_triplet_dataset import TripletFmaDataset
from muq import MuQ

# --- 설정 (Configuration) ---
# GPU 사용 가능 여부 확인
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# 경로 설정 (Paths)
# 학습에 사용할 메타데이터 JSONL 파일 경로 (훈련셋)
JSONL_PATH = '/home/jay/MusicAI/MUSEED/data/train_metadata.jsonl'
# 오디오 파일들이 저장된 디렉토리 경로
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
# 학습된 모델이 저장될 디렉토리
MODEL_SAVE_DIR = '/home/jay/MusicAI/MUSEED/models/'
# 저장될 모델 파일 이름
MODEL_NAME = "muq_finetuned_triplet_float32_v1.pth"
# 텐서보드 로그 저장 경로
LOG_DIR = "runs/fma_triplet_finetuning_v1"

# 하이퍼파라미터 (Hyperparameters)
LEARNING_RATE = 1e-5  # 학습률 (v3: 1e-6)
BATCH_SIZE = 16      # 배치 크기 (Float32 사용을 위해 16으로 설정)
NUM_EPOCHS = 5        # 학습 에포크 수
MARGIN = 0.20         # Triplet Loss의 마진 값 (유사도 차이의 최소 기준)
NUM_WORKERS = 4       # 데이터 로더 워커 수

def train():
    """
    MuQ 모델 파인튜닝 메인 학습 함수
    Triplet Margin Loss 사용하여 오디오 임베딩 공간 학습
    """
    print(f"Using device: {DEVICE}")
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    # 타임스탬프 포함 고유 로그 디렉토리 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_log_dir = os.path.join(LOG_DIR, timestamp)
    print(f"TensorBoard logs will be saved to: {unique_log_dir}")
    writer = SummaryWriter(unique_log_dir)

    # 1. 모델 로드
    print("Loading MuQ model for fine-tuning...")
    # 사전 학습된 MuQ 모델 로드
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)

    # --- 부분 파인튜닝 (Partial Fine-tuning) 설정 ---
    print("\n--- Setting up partial fine-tuning ---")
    # 우선 모든 파라미터 학습 동결(Freeze)
    for param in model.parameters():
        param.requires_grad = False
    
    # 특정 레이어만 학습 설정 (Conformer 6~11번 레이어 및 Linear 헤드)
    for i in range(6, 12):
        for param in model.model.conformer.layers[i].parameters():
            param.requires_grad = True
    for param in model.model.linear.parameters():
        param.requires_grad = True

    # 학습될 파라미터 수 확인
    params_to_update = [p for p in model.parameters() if p.requires_grad]
    print(f"Training {len(params_to_update)} parameter tensors.")

    # 2. 데이터셋 및 데이터로더 초기화
    print("Initializing TripletFmaDataset...")
    try:
        # 커스텀 데이터셋 클래스 인스턴스 생성
        dataset = TripletFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR)
        dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    except Exception as e:
        print(f"Error initializing dataset: {e}")
        writer.close()
        return

    # 3. 옵티마이저 및 손실 함수 정의
    optimizer = AdamW(params_to_update, lr=LEARNING_RATE)
    # Triplet Margin Loss: max(d(a, p) - d(a, n) + margin, 0)
    triplet_loss_fn = nn.TripletMarginLoss(margin=MARGIN, p=2)

    print("\n--- Starting Training in Full Float32 Precision ---")
    model.train() # 학습 모드 전환

    try:
        global_step = 0
        for epoch in range(NUM_EPOCHS):
            total_loss = 0.0
            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}")

            # 배치 단위 학습 루프
            for anchor_audio, positive_audio, negative_audio in progress_bar:
                # 데이터를 GPU로 이동
                anchor_audio = anchor_audio.to(DEVICE)
                positive_audio = positive_audio.to(DEVICE)
                negative_audio = negative_audio.to(DEVICE)

                optimizer.zero_grad()

                # 순전파 (Forward Pass)
                # [:, 0, :]는 시퀀스의 첫 번째 토큰(CLS 토큰 유사)을 임베딩 사용
                anchor_embed = model(anchor_audio).last_hidden_state[:, 0, :]
                positive_embed = model(positive_audio).last_hidden_state[:, 0, :]
                negative_embed = model(negative_audio).last_hidden_state[:, 0, :]
                
                # 손실 계산 (Calculate Loss)
                loss = triplet_loss_fn(anchor_embed, positive_embed, negative_embed)

                # 역전파 (Backward Pass) 및 가중치 업데이트
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})

                # 텐서보드에 스텝별 손실 기록
                writer.add_scalar('Loss/step', loss.item(), global_step)
                global_step += 1

            # 에포크 종료 후 평균 손실 출력 및 기록
            avg_loss = total_loss / len(dataloader)
            print(f"\nEnd of Epoch {epoch + 1}, Average Loss: {avg_loss:.4f}")
            writer.add_scalar('Loss/epoch', avg_loss, epoch)

    except KeyboardInterrupt:
        # 사용자 중단(Ctrl+C) 시 현재 상태 저장
        print("\n\n--- Training interrupted by user. Saving current model state... ---")
        save_path = os.path.join(MODEL_SAVE_DIR, f"interrupted_{MODEL_NAME}")
        torch.save(model.state_dict(), save_path)
        print(f"Model saved to {save_path}")
        writer.close()
        return

    # --- 학습 완료 후 모델 저장 ---
    print("\n--- Training Finished ---")
    save_path = os.path.join(MODEL_SAVE_DIR, MODEL_NAME)
    torch.save(model.state_dict(), save_path)
    print(f"Fine-tuned model saved to {save_path}")
    
    writer.close()

if __name__ == '__main__':
    train()

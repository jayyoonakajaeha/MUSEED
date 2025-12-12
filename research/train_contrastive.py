import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import os
from datetime import datetime

from fma_contrastive_dataset import ContrastiveFmaDataset
from contrastive_loss import NTXentLoss
from muq import MuQ

# --- 설정 (Configuration) ---
# GPU 사용 가능 여부 확인
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# 경로 설정 (Paths)
JSONL_PATH = '/home/jay/MusicAI/MUSEED/data/train_metadata.jsonl'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
MODEL_SAVE_DIR = '/home/jay/MusicAI/MUSEED/models/'
MODEL_NAME = "muq_contrastive_simclr_v2.pth"
LOG_DIR = "runs/fma_contrastive_v2"

# 하이퍼파라미터 (Hyperparameters)
LEARNING_RATE = 1e-5       
BATCH_SIZE = 16            # 마이크로 배치 크기 (VRAM 용량에 맞춰 설정)
GRAD_ACCUM_STEPS = 4       # 유효 배치 크기 (Effective Batch Size) = 16 * 4 = 64
NUM_EPOCHS = 5
TEMPERATURE = 0.1          # Contrastive Loss의 온도 파라미터
NUM_WORKERS = 4
PROJECTION_DIM = 128       # 투영 헤드 차원

class MuQContrastive(nn.Module):
    """
    SimCLR 스타일 Contrastive Learning용 MuQ 래퍼 클래스
    기본 인코더(MuQ) 위에 비선형 투영 헤드(Projection Head) 추가
    """
    def __init__(self, base_model, embedding_dim=1024, projection_dim=128):
        super().__init__()
        self.encoder = base_model
        # 투영 헤드: 임베딩 공간을 Contrastive Loss 최적화 공간으로 매핑
        self.projection_head = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, projection_dim)
        )

    def forward(self, x):
        # 인코더 통과 후 표현 벡터 추출
        outputs = self.encoder(x)
        # [CLS] 토큰 유사 첫 번째 토큰 임베딩 사용
        embedding = outputs.last_hidden_state[:, 0, :]
        # 투영 헤드 통과 후 최종 비교용 벡터 생성
        projected = self.projection_head(embedding)
        return embedding, projected

def train():
    """
    Contrastive Learning (SimCLR) 학습 실행 메인 함수
    메모리 효율성 위한 Gradient Cache 전략 사용
    """
    print(f"Using device: {DEVICE}")
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_log_dir = os.path.join(LOG_DIR, timestamp)
    print(f"TensorBoard logs: {unique_log_dir}")
    writer = SummaryWriter(unique_log_dir)

    # 1. 베이스 모델 로드
    print("Loading MuQ base model...")
    base_model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
    
    model = MuQContrastive(base_model).to(DEVICE)

    # --- 동결(Freezing) 전략 ---
    # 우선 모든 파라미터 동결
    for param in model.parameters():
        param.requires_grad = False
    
    # 투영 헤드(Projection Head) 학습 위해 동결 해제
    for param in model.projection_head.parameters():
        param.requires_grad = True
        
    # Conformer 상위 2개 레이어만 동결 해제 (Partial Fine-tuning)
    conformer_layers = model.encoder.model.conformer.layers
    num_layers = len(conformer_layers)
    print(f"Detected {num_layers} Conformer layers.")
    
    for i in range(num_layers - 2, num_layers):
        print(f"Unfreezing Conformer Layer {i}")
        for param in conformer_layers[i].parameters():
            param.requires_grad = True
            
    # Linear 레이어 동결 해제
    for param in model.encoder.model.linear.parameters():
        param.requires_grad = True
    
    params_to_update = [p for p in model.parameters() if p.requires_grad]
    print(f"Training {len(params_to_update)} tensors.")

    # 2. 데이터셋 설정 (장르 균형 적용)
    # 속도 및 균형 위해 장르당 500개 샘플 사용
    dataset = ContrastiveFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR, max_samples_per_genre=2000)
    
    # Gradient Accumulation 시 배치 일치 필요하므로 drop_last=True 사용
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, 
                            num_workers=NUM_WORKERS, pin_memory=True, drop_last=True)

    # 3. 최적화 설정
    optimizer = AdamW(params_to_update, lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS * len(dataloader) // GRAD_ACCUM_STEPS, eta_min=1e-7)
    criterion = NTXentLoss(temperature=TEMPERATURE)

    print("\n--- Starting Contrastive Training (Gradient Cache Strategy) ---")
    print(f"Micro Batch: {BATCH_SIZE}, Accum Steps: {GRAD_ACCUM_STEPS}, Effective Batch: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
    model.train()
    
    global_step = 0
    
    try:
        # 데이터로더 청크 반복용 헬퍼 설정
        dataloader_iter = iter(dataloader)
        total_steps = len(dataloader) // GRAD_ACCUM_STEPS
        
        for epoch in range(NUM_EPOCHS):
            total_epoch_loss = 0.0
            
            # 에폭마다 이터레이터 초기화
            dataloader_iter = iter(dataloader)
            
            progress_bar = tqdm(range(total_steps), desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}")
            
            for _ in progress_bar:
                optimizer.zero_grad()
                
                # Gradient Cache용 버퍼
                micro_inputs_1 = []
                micro_inputs_2 = []
                cache_proj_1 = []
                cache_proj_2 = []
                
                # === 1단계: 임베딩 누적 (Forward Pass - No Grad) ===
                # VRAM 절약하며 "전역 컨텍스트" 구축 위해 그래디언트 없이 Forward 수행
                model.eval() # 메모리 절약용 eval 모드 (SimCLR에서는 보통 유지하나 여기선 VRAM 최적화 우선)
                
                with torch.no_grad():
                    for _ in range(GRAD_ACCUM_STEPS):
                        try:
                            view1, view2 = next(dataloader_iter)
                        except StopIteration:
                            break
                        
                        view1 = view1.to(DEVICE)
                        view2 = view2.to(DEVICE)
                        
                        # 3단계(Backward) 위해 입력 데이터 저장
                        # VRAM 부족 시 CPU로 옮겨야 하나 배치(16)가 작으므로 GPU 유지
                        micro_inputs_1.append(view1)
                        micro_inputs_2.append(view2)
                        
                        _, proj1 = model(view1)
                        _, proj2 = model(view2)
                        
                        cache_proj_1.append(proj1)
                        cache_proj_2.append(proj2)

                if len(cache_proj_1) == 0: break

                # === 2단계: 전역 손실 계산 (Global Loss Calculation) ===
                # 모든 마이크로 배치 임베딩 합쳐 유효 배치(Effective Batch) 생성
                full_proj_1 = torch.cat(cache_proj_1, dim=0)
                full_proj_2 = torch.cat(cache_proj_2, dim=0)
                
                # 이 텐서들에 대해서만 그래디언트 계산 설정
                full_proj_1.requires_grad = True
                full_proj_2.requires_grad = True
                
                loss = criterion(full_proj_1, full_proj_2)
                loss.backward() # full_proj_1, full_proj_2에 대한 그래디언트 계산
                
                total_epoch_loss += loss.item()
                
                # === 3단계: 로컬 역전파 (Local Backward - Gradient Cache) ===
                # 계산된 전역 그래디언트를 각 마이크로 배치로 전파
                model.train()
                
                for i in range(len(micro_inputs_1)):
                    inputs1 = micro_inputs_1[i]
                    inputs2 = micro_inputs_2[i]
                    
                    # 현재 마이크로 배치 해당 그래디언트 슬라이싱
                    start_idx = i * BATCH_SIZE
                    end_idx = (i + 1) * BATCH_SIZE
                    
                    grad_1 = full_proj_1.grad[start_idx:end_idx]
                    grad_2 = full_proj_2.grad[start_idx:end_idx]
                    
                    # 그래디언트 추적 켜고 다시 Forward 수행
                    _, p1 = model(inputs1)
                    _, p2 = model(inputs2)
                    
                    # Surrogate Backward: 캐시된 그래디언트 주입하여 역전파 수행
                    # 전체 배치 한 번에 올리지 않고도 동일 학습 효과
                    torch.autograd.backward([p1, p2], [grad_1, grad_2])
                
                # 가중치 업데이트
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                
                # 로그 기록
                progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
                writer.add_scalar('Loss/step', loss.item(), global_step)
                writer.add_scalar('LR', scheduler.get_last_lr()[0], global_step)
                global_step += 1

            avg_loss = total_epoch_loss / total_steps
            print(f"Epoch {epoch+1} Average Loss: {avg_loss:.4f}")
            writer.add_scalar('Loss/epoch', avg_loss, epoch)
            
            # 체크포인트 저장
            torch.save(model.encoder.state_dict(), os.path.join(MODEL_SAVE_DIR, f"checkpoint_epoch_{epoch+1}.pth"))

    except KeyboardInterrupt:
        print("\n--- 사용자 중단에 의한 학습 종료. 현재 상태 저장... ---")
        save_path = os.path.join(MODEL_SAVE_DIR, f"interrupted_{MODEL_NAME}")
        torch.save(model.encoder.state_dict(), save_path)
        print(f"모델 저장됨: {save_path}")
        writer.close()
        return

    # --- 최종 모델 저장 ---
    print("\n--- 학습 완료 (Training Finished) ---")
    save_path = os.path.join(MODEL_SAVE_DIR, MODEL_NAME)
    torch.save(model.encoder.state_dict(), save_path)
    print(f"최종 모델 저장됨: {save_path}")
    writer.close()

if __name__ == "__main__":
    train()

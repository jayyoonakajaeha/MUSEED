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

# --- Configuration ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Paths
JSONL_PATH = '/home/jay/MusicAI/multi_axis_analysis_results.jsonl'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
MODEL_SAVE_DIR = '/home/jay/MusicAI/MuQ/finetuned_models/'
MODEL_NAME = "muq_contrastive_simclr_v1.pth"
LOG_DIR = "runs/fma_contrastive_v1"

# Hyperparameters
LEARNING_RATE = 1e-5       # Lower LR for stability
BATCH_SIZE = 16            # Physical batch size
GRAD_ACCUM_STEPS = 4       # Effective batch size = 64
NUM_EPOCHS = 5
TEMPERATURE = 0.1
NUM_WORKERS = 4
PROJECTION_DIM = 128

class MuQContrastive(nn.Module):
    def __init__(self, base_model, embedding_dim=1024, projection_dim=128):
        super().__init__()
        self.encoder = base_model
        self.projection_head = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, projection_dim)
        )

    def forward(self, x):
        outputs = self.encoder(x)
        embedding = outputs.last_hidden_state[:, 0, :]
        projected = self.projection_head(embedding)
        return embedding, projected

def train():
    print(f"Using device: {DEVICE}")
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_log_dir = os.path.join(LOG_DIR, timestamp)
    print(f"TensorBoard logs: {unique_log_dir}")
    writer = SummaryWriter(unique_log_dir)

    # 1. Load Base Model
    print("Loading MuQ base model...")
    base_model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
    
    model = MuQContrastive(base_model).to(DEVICE)

    # --- Freezing Strategy ---
    for param in model.parameters():
        param.requires_grad = False
    
    # Unfreeze Projection Head
    for param in model.projection_head.parameters():
        param.requires_grad = True
        
    # Unfreeze Top 2 Conformer Layers
    conformer_layers = model.encoder.model.conformer.layers
    num_layers = len(conformer_layers)
    print(f"Detected {num_layers} Conformer layers.")
    
    for i in range(num_layers - 2, num_layers):
        print(f"Unfreezing Conformer Layer {i}")
        for param in conformer_layers[i].parameters():
            param.requires_grad = True
            
    for param in model.encoder.model.linear.parameters():
        param.requires_grad = True
    
    params_to_update = [p for p in model.parameters() if p.requires_grad]
    print(f"Training {len(params_to_update)} tensors.")

    # 2. Dataset
    dataset = ContrastiveFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, 
                            num_workers=NUM_WORKERS, pin_memory=True, drop_last=True)

    # 3. Optimization
    optimizer = AdamW(params_to_update, lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS * len(dataloader), eta_min=1e-7)
    criterion = NTXentLoss(temperature=TEMPERATURE)

    print("\n--- Starting Contrastive Training (Float32) ---")
    model.train()
    
    global_step = 0
    
    try:
        for epoch in range(NUM_EPOCHS):
            total_loss = 0.0
            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}")
            
            optimizer.zero_grad()
            
            for i, (view1, view2) in enumerate(progress_bar):
                view1 = view1.to(DEVICE)
                view2 = view2.to(DEVICE)
                
                # Forward (No autocast)
                _, proj1 = model(view1)
                _, proj2 = model(view2)
                
                loss = criterion(proj1, proj2)
                loss = loss / GRAD_ACCUM_STEPS 
                
                # Backward (No scaler)
                loss.backward()
                
                if (i + 1) % GRAD_ACCUM_STEPS == 0:
                    # Gradient Clipping
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
                
                current_loss = loss.item() * GRAD_ACCUM_STEPS
                
                if torch.isnan(torch.tensor(current_loss)):
                    print(f"Warning: NaN loss at step {global_step}")
                else:
                    total_loss += current_loss

                progress_bar.set_postfix({'loss': f'{current_loss:.4f}'})
                writer.add_scalar('Loss/step', current_loss, global_step)
                writer.add_scalar('LR', scheduler.get_last_lr()[0], global_step)
                global_step += 1

            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1} Average Loss: {avg_loss:.4f}")
            writer.add_scalar('Loss/epoch', avg_loss, epoch)
            
            torch.save(model.encoder.state_dict(), os.path.join(MODEL_SAVE_DIR, f"checkpoint_epoch_{epoch+1}.pth"))

    except KeyboardInterrupt:
        print("Training interrupted.")
    
    torch.save(model.encoder.state_dict(), os.path.join(MODEL_SAVE_DIR, MODEL_NAME))
    print(f"Model saved to {os.path.join(MODEL_SAVE_DIR, MODEL_NAME)}")
    writer.close()

if __name__ == "__main__":
    train()
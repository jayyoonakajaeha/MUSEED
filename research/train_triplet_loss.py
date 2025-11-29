
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

# --- Configuration ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Paths
JSONL_PATH = '/home/jay/MusicAI/MUSEED/research/results/multi_axis_analysis_results.jsonl'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
MODEL_SAVE_DIR = '/home/jay/MusicAI/MUSEED/models/'
MODEL_NAME = "muq_finetuned_triplet_float32_v3.pth"
LOG_DIR = "runs/fma_triplet_finetuning_v3"

# Hyperparameters
LEARNING_RATE = 1e-6 # v1: 1e-6, v2: 1e-5, v3: 1e-6
BATCH_SIZE = 16      # Smaller batch size for float32 VRAM usage
NUM_EPOCHS = 3 # v1: 2, v2: 3, v3: 3
MARGIN = 0.25 # v1: 0.2, v2: 0.3, v3: 0.25
NUM_WORKERS = 4

def train():
    print(f"Using device: {DEVICE}")
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    # Create a unique log directory with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_log_dir = os.path.join(LOG_DIR, timestamp)
    print(f"TensorBoard logs will be saved to: {unique_log_dir}")
    writer = SummaryWriter(unique_log_dir)

    # 1. Model
    print("Loading MuQ model for fine-tuning...")
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)

    # --- Partial Fine-tuning ---
    print("\n--- Setting up partial fine-tuning ---")
    for param in model.parameters():
        param.requires_grad = False
    for i in range(6, 12):
        for param in model.model.conformer.layers[i].parameters():
            param.requires_grad = True
    for param in model.model.linear.parameters():
        param.requires_grad = True

    params_to_update = [p for p in model.parameters() if p.requires_grad]
    print(f"Training {len(params_to_update)} parameter tensors.")

    # 2. Dataset and DataLoader
    print("Initializing TripletFmaDataset...")
    try:
        dataset = TripletFmaDataset(jsonl_path=JSONL_PATH, audio_dir=AUDIO_DIR)
        dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    except Exception as e:
        print(f"Error initializing dataset: {e}")
        writer.close()
        return

    # 3. Optimizer and Loss Function
    optimizer = AdamW(params_to_update, lr=LEARNING_RATE)
    triplet_loss_fn = nn.TripletMarginLoss(margin=MARGIN, p=2)

    print("\n--- Starting Training in Full Float32 Precision ---")
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

                # Standard forward pass
                anchor_embed = model(anchor_audio).last_hidden_state[:, 0, :]
                positive_embed = model(positive_audio).last_hidden_state[:, 0, :]
                negative_embed = model(negative_audio).last_hidden_state[:, 0, :]
                
                loss = triplet_loss_fn(anchor_embed, positive_embed, negative_embed)

                # Standard backward pass
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
        print("\n\n--- Training interrupted by user. Saving current model state... ---")
        save_path = os.path.join(MODEL_SAVE_DIR, f"interrupted_{MODEL_NAME}")
        torch.save(model.state_dict(), save_path)
        print(f"Model saved to {save_path}")
        writer.close()
        return

    # --- Save the fine-tuned model ---
    print("\n--- Training Finished ---")
    save_path = os.path.join(MODEL_SAVE_DIR, MODEL_NAME)
    torch.save(model.state_dict(), save_path)
    print(f"Fine-tuned model saved to {save_path}")
    
    writer.close()

if __name__ == '__main__':
    train()

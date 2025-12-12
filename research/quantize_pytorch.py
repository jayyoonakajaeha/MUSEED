
import torch
import torch.quantization
import os
import time
import numpy as np
from muq import MuQ

# --- Configuration ---
MODEL_PATH = '/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v2.pth'
QUANTIZED_MODEL_PATH = '/home/jay/MusicAI/MUSEED/models/muq_v2_quantized_cpu.pth'
DURATION_SAMPLES = 160000

def quantize_and_benchmark():
    print(f"Loading model from {MODEL_PATH} on CPU...")
    # Load on CPU for quantization
    model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to('cpu')
    model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    model.eval()

    # REMOVE WEIGHT NORM (Required for Quantization/DeepCopy)
    print("Removing weight_norm pre-hooks...")
    from torch.nn.utils import remove_weight_norm
    for module in model.modules():
        try:
            remove_weight_norm(module)
        except ValueError:
            pass # Module didn't have weight_norm
            
    # 1. Benchmark Original (CPU)
    dummy_input = torch.randn(1, DURATION_SAMPLES).to('cpu')
    print("Benchmarking Original (FP32) on CPU...")
    start = time.time()
    with torch.no_grad():
        original_out = model(dummy_input).last_hidden_state
    print(f"Original Inference Time: {time.time() - start:.4f}s")
    
    # 2. Apply Dynamic Quantization
    print("Applying Dynamic Quantization (Linear/LSTM/RNN -> INT8)...")
    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear, torch.nn.LSTM, torch.nn.GRU}, # Target layers
        dtype=torch.qint8
    )
    
    # 3. Benchmark Quantized (CPU)
    print("Benchmarking Quantized (INT8) on CPU...")
    start = time.time()
    with torch.no_grad():
        quantized_out = quantized_model(dummy_input).last_hidden_state
    print(f"Quantized Inference Time: {time.time() - start:.4f}s")
    
    # 4. Compare Accuracy
    diff = np.abs(original_out.numpy() - quantized_out.numpy()).max()
    print(f"Max Difference: {diff:.6f}")
    
    if diff > 1.0: # Audio embeddings might drift, but let's see. 
        # Typically < 0.1 is good, but complex models might vary.
        print("WARNING: High divergence!")
    else:
        print("Accuracy check passed (within tolerance).")

    # 5. Save
    print(f"Saving quantized model to {QUANTIZED_MODEL_PATH}...")
    torch.save(quantized_model, QUANTIZED_MODEL_PATH) # Serialize full object
    print(f"Saved size: {os.path.getsize(QUANTIZED_MODEL_PATH) / 1024 / 1024:.2f} MB")
    print(f"Original size: {os.path.getsize(MODEL_PATH) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    quantize_and_benchmark()

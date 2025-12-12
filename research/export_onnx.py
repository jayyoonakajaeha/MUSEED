
import torch
import torch.onnx
import onnx
import onnxruntime
import numpy as np
import os
from muq import MuQ

# --- Configuration ---
MODEL_PATH = '/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v2.pth'
ONNX_PATH = '/home/jay/MusicAI/MUSEED/models/muq_v2.onnx'
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def export_model():
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter").to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # Create dummy input
    dummy_input = torch.randn(1, DURATION_SAMPLES).to(DEVICE)

    # Wrapper class to just return embedding (simplifies ONNX graph)
    class ModelWrapper(torch.nn.Module):
        def __init__(self, original_model):
            super().__init__()
            self.model = original_model
        
        def forward(self, x):
            # Same logic as playlists.py/worker.py
            output = self.model(x)
            # return output.last_hidden_state[:, 0, :] # Extract embedding
            # Wait, let's export the full last_hidden_state first, and slice outside? 
            # Or export exact logic? Exact logic is better for drop-in replacement.
            return output.last_hidden_state[:, 0, :]

    wrapped_model = ModelWrapper(model).to(DEVICE)

    print(f"Exporting to ONNX: {ONNX_PATH}...")
    try:
        torch.onnx.export(
            wrapped_model,
            dummy_input,
            ONNX_PATH,
            export_params=True,
            opset_version=17, # Supports STFT
            do_constant_folding=True,
            input_names=['input'],
            output_names=['embedding'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'embedding': {0: 'batch_size'}
            }
        )
        print("Export successful!")
    except Exception as e:
        print(f"Export failed: {e}")
        return

    # --- Verification ---
    print("Verifying ONNX model...")
    try:
        onnx_model = onnx.load(ONNX_PATH)
        onnx.checker.check_model(onnx_model)
        print("ONNX structure check passed.")
        
        # Inference Check
        ort_session = onnxruntime.InferenceSession(ONNX_PATH, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        
        # PyTorch Output
        with torch.no_grad():
            torch_out = wrapped_model(dummy_input).cpu().numpy()
            
        # ONNX Output
        ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.cpu().numpy()}
        ort_out = ort_session.run(None, ort_inputs)[0]
        
        # Compare
        delta = np.abs(torch_out - ort_out).max()
        print(f"Max difference between PyTorch and ONNX: {delta}")
        
        if delta < 1e-4:
            print("Verification PASSED: Outputs match.")
        else:
            print("Verification FAILED: Outputs diverge significantly.")
            
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    export_model()

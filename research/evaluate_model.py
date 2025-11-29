import torch
import pandas as pd
import torchaudio
import os
import numpy as np
from tqdm import tqdm
import random
import argparse
import json
from collections import defaultdict

# Evaluation specific imports
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, silhouette_score, classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

from muq import MuQ, MuQConfig

# --- Configuration ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
AUDIO_DIR = '/home/jay/MusicAI/fma/data/fma_full'
BASE_MUQ_EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings_base_muq/'
FINETUNED_MUQ_EMBEDDING_DIR = '/home/jay/MusicAI/fma_audio_embeddings_finetuned_muq_v3/'
DEFAULT_FINETUNED_MODEL_PATH = '/home/jay/MusicAI/MuQ/finetuned_models/muq_finetuned_triplet_float32_v3.pth'
JSONL_PATH = '/home/jay/MusicAI/MUSEED/research/results/multi_axis_analysis_results.jsonl'
RESULTS_JSON_PATH = 'results/evaluation_results_v3.json' # Path to save results
SAMPLE_RATE = 16000
DURATION_SAMPLES = 160000  # 10 seconds
AXES_TO_EVALUATE = ['genre', 'source', 'valence', 'energy', 'mood_style']


# --- Audio Preprocessing ---
def load_and_preprocess_audio(file_path):
    """Loads and preprocesses a single audio file."""
    try:
        waveform, sr = torchaudio.load(file_path)
        if sr != SAMPLE_RATE:
            waveform = torchaudio.functional.resample(waveform, sr, SAMPLE_RATE)
        
        # Convert to mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Pad or truncate
        if waveform.shape[1] < DURATION_SAMPLES:
            padding = DURATION_SAMPLES - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
        else:
            waveform = waveform[:, :DURATION_SAMPLES]
            
        return waveform.to(DEVICE)
    except Exception as e:
        print(f"Warning: Could not load or process audio file {os.path.basename(file_path)}: {e}")
        return None

# --- Embedding Generation ---
def generate_embeddings(model_path, output_dir):
    """Generates and saves embeddings for all tracks found in the JSONL metadata."""
    print(f"\n{'='*20} Generating Embeddings {'='*20}")
    print(f"Model: {model_path}")
    print(f"Output Directory: {output_dir}")

    # 1. Load Model
    print("\nLoading model...")
    try:
        # First, load the base model architecture and config from the pretrained source.
        # This ensures the architecture is correct.
        print("Loading base model architecture from 'OpenMuQ/MuQ-large-msd-iter'...")
        model = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
        
        # Now, load the fine-tuned weights into the model.
        print(f"Loading fine-tuned state dict from {model_path}...")
        model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        
        model.to(DEVICE)
        model.eval()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error: Could not load model from {model_path}. {e}")
        return

    # 2. Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # 3. Get list of tracks to process from JSONL
    track_ids_to_process = set()
    try:
        with open(JSONL_PATH, 'r') as f:
            for line in f:
                data = json.loads(line)
                track_ids_to_process.add(str(data['track_id']))
        print(f"Found {len(track_ids_to_process)} tracks to process from metadata file.")
    except FileNotFoundError:
        print(f"Error: Metadata file not found at {JSONL_PATH}")
        return

    # 4. Process audio files and save embeddings
    print("\nProcessing audio files and generating embeddings...")
    with torch.no_grad():
        for track_id in tqdm(track_ids_to_process, desc="Generating Embeddings"):
            # Format track_id to match FMA directory structure (e.g., '000002' -> '000/000002.mp3')
            track_id_str = track_id.zfill(6)
            subdir = track_id_str[:3]
            audio_file_path = os.path.join(AUDIO_DIR, subdir, f"{track_id_str}.mp3")
            output_path = os.path.join(output_dir, f"{track_id}.npy")

            if not os.path.exists(audio_file_path):
                # print(f"Warning: Audio file not found for track {track_id}, skipping.")
                continue
            
            if os.path.exists(output_path):
                # print(f"Embedding for track {track_id} already exists, skipping.")
                continue

            waveform = load_and_preprocess_audio(audio_file_path)
            if waveform is None:
                continue

            # Get embedding using the model's forward pass
            output = model(waveform, output_hidden_states=False)
            # Average across the time dimension to get a single vector
            embedding = output.last_hidden_state.mean(dim=1)
            embedding_np = embedding.squeeze().cpu().numpy()

            # Save embedding
            np.save(output_path, embedding_np)
    
    print(f"\n--- Embedding Generation Complete! Embeddings saved to {output_dir} ---")


# --- Data Loading for Evaluation ---
def load_embeddings_and_labels(embedding_dir):
    """Loads embeddings and corresponding labels for multiple axes."""
    print(f"\nLoading data from {embedding_dir}...")
    embeddings = []
    labels = defaultdict(list)
    track_ids = []

    # Load track metadata from JSONL into a dictionary for quick lookup
    track_metadata = {}
    try:
        with open(JSONL_PATH, 'r') as f:
            for line in f:
                data = json.loads(line)
                track_id = str(data['track_id'])
                metadata_for_track = {}
                for axis in AXES_TO_EVALUATE:
                    if axis == 'source':
                        metadata_for_track[axis] = data.get('instrumentation', {}).get(axis)
                    elif axis in ['valence', 'energy']:
                        metadata_for_track[axis] = data.get('affect', {}).get(axis)
                    else: # genre, mood_style (top-level)
                        metadata_for_track[axis] = data.get(axis)
                track_metadata[track_id] = metadata_for_track
    except FileNotFoundError:
        print(f"Error: Metadata file not found at {JSONL_PATH}")
        return None, None, None

    # Iterate through available embedding files
    embedding_files = [f for f in os.listdir(embedding_dir) if f.endswith('.npy')]
    for filename in tqdm(embedding_files, desc="Loading embeddings and labels"):
        track_id_str = os.path.splitext(filename)[0]
        
        # Check if metadata exists for this track
        if track_id_str in track_metadata:
            try:
                embedding = np.load(os.path.join(embedding_dir, filename))
                if embedding.ndim == 1:
                    embeddings.append(embedding)
                    track_axes = track_metadata[track_id_str]
                    for axis in AXES_TO_EVALUATE:
                        labels[axis].append(track_axes.get(axis)) # Will append None if axis is missing
                    track_ids.append(int(track_id_str))
            except Exception as e:
                print(f"Warning: Could not load or process embedding for track {track_id_str}: {e}")

    if not embeddings:
        print(f"Error: No embeddings found or matched with metadata in {embedding_dir}.")
        return None, None, None

    return np.array(embeddings), dict(labels), track_ids

# --- Evaluation Logic ---
def run_evaluation_for_model(embedding_path, model_name):
    """Runs the full evaluation suite for a given set of embeddings and returns results as a dict."""
    print(f"\n{'='*20} Evaluating: {model_name} {'='*20}")
    results = {'model_name': model_name}

    # 1. Load Data
    X, y_all_axes, _ = load_embeddings_and_labels(embedding_path)
    if X is None:
        return None

    # 2. k-NN Classification (on Genre)
    print("\n--- Running k-NN Classification (on Genre) ---")
    # Filter data for entries that have a genre label
    genre_labels = np.array(y_all_axes['genre'])
    valid_indices_genre = [i for i, label in enumerate(genre_labels) if label is not None]
    X_genre = X[valid_indices_genre]
    y_genre = genre_labels[valid_indices_genre]

    if len(X_genre) > 0:
        le_genre = LabelEncoder()
        y_genre_encoded = le_genre.fit_transform(y_genre)
        
        X_train, X_test, y_train_genre, y_test_genre = train_test_split(X_genre, y_genre_encoded, test_size=0.2, random_state=42, stratify=y_genre_encoded)
        print(f"Data split for genre classification: {len(X_train)} train, {len(X_test)} test samples.")
        
        knn = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
        knn.fit(X_train, y_train_genre)
        y_pred_genre = knn.predict(X_test)
        
        accuracy = accuracy_score(y_test_genre, y_pred_genre)
        results['knn_accuracy_genre'] = accuracy
        print(f"\nOverall k-NN Accuracy (Genre): {accuracy:.4f}")
        
        class_names = le_genre.inverse_transform(np.arange(len(le_genre.classes_)))
        report = classification_report(y_test_genre, y_pred_genre, target_names=class_names, zero_division=0, output_dict=True)
        results['classification_report_genre'] = report
    else:
        print("No valid genre labels found for k-NN classification.")
        results['knn_accuracy_genre'] = "N/A"


    # 3. Silhouette Score for all axes
    print("\n--- Calculating Silhouette Scores for All Axes ---")
    results['silhouette_scores'] = {}
    
    for axis in AXES_TO_EVALUATE:
        print(f"  - Processing axis: {axis}")
        try:
            # Filter data for the current axis
            axis_labels = np.array(y_all_axes[axis])
            valid_indices_axis = [i for i, label in enumerate(axis_labels) if label is not None]
            
            if len(valid_indices_axis) < 10: # Need at least a few points
                print(f"    Not enough data to calculate score for {axis}.")
                continue

            X_axis = X[valid_indices_axis]
            y_axis = axis_labels[valid_indices_axis]

            le_axis = LabelEncoder()
            y_axis_encoded = le_axis.fit_transform(y_axis)

            # Check if there's more than 1 unique label
            if len(np.unique(y_axis_encoded)) <= 1:
                error_msg = "Only 1 class present, cannot calculate score."
                results['silhouette_scores'][axis] = f"Error: {error_msg}"
                print(f"    Could not calculate silhouette score for {axis}: {error_msg}")
                continue

            # Take a sample for efficiency
            sample_size = min(50000,len(X_axis))
            random_indices = np.random.choice(len(X_axis), sample_size, replace=False)
            X_sample = X_axis[random_indices]
            y_sample = y_axis_encoded[random_indices]

            print(f"    Calculating score on a sample of {sample_size} data points for axis '{axis}'...")
            silhouette = silhouette_score(X_sample, y_sample, metric='cosine')
            results['silhouette_scores'][axis] = silhouette
            print(f"    Silhouette Score ({axis}): {silhouette:.4f}")

        except Exception as e:
            results['silhouette_scores'][axis] = f"Error: {e}"
            print(f"    Could not calculate silhouette score for {axis}: {e}")


    # 4. t-SNE Visualization (on Genre)
    print("\n--- Generating t-SNE Visualization (on Genre) ---")
    if len(X_genre) > 0:
        tsne_sample_size = min(8000, len(X_genre))
        tsne_indices = np.random.choice(len(X_genre), tsne_sample_size, replace=False)
        X_tsne_sample = X_genre[tsne_indices]
        y_tsne_sample_labels = y_genre[tsne_indices]

        print(f"Running t-SNE on {tsne_sample_size} data points...")
        tsne = TSNE(n_components=2, verbose=1, perplexity=40, max_iter=300, random_state=42)
        tsne_results = tsne.fit_transform(X_tsne_sample)

        df_tsne = pd.DataFrame()
        df_tsne['tsne-2d-one'] = tsne_results[:,0]
        df_tsne['tsne-2d-two'] = tsne_results[:,1]
        df_tsne['genre'] = y_tsne_sample_labels
        
        print("Plotting results...")
        plt.figure(figsize=(16,10))
        sns.scatterplot(
            x="tsne-2d-one", y="tsne-2d-two",
            hue="genre",
            palette=sns.color_palette("hsv", len(np.unique(y_tsne_sample_labels))),
            data=df_tsne,
            legend="full",
            alpha=0.7
        )
        plt.title(f't-SNE Visualization for {model_name} (colored by Genre)')
        
        plot_filename = f"plots/tsne_{model_name}.png"
        plt.savefig(plot_filename)
        print(f"t-SNE plot saved to {plot_filename}")
        plt.close()
    else:
        print("No valid genre labels found for t-SNE visualization.")
    
    return results


def evaluate_models():
    """Main evaluation function to compare models."""
    all_results = []
    
    print("Starting evaluation for Base MuQ model...")
    base_results = run_evaluation_for_model(BASE_MUQ_EMBEDDING_DIR, 'base_muq')
    if base_results:
        all_results.append(base_results)
    
    print("\n\nStarting evaluation for Fine-tuned MuQ model...")
    finetuned_results = run_evaluation_for_model(FINETUNED_MUQ_EMBEDDING_DIR, 'finetuned_muq_v3') # graph name
    if finetuned_results:
        all_results.append(finetuned_results)
    
    # Save results to JSON file
    with open(RESULTS_JSON_PATH, 'w') as f:
        json.dump(all_results, f, indent=4)
    print(f"\n--- Evaluation Complete! Results saved to {RESULTS_JSON_PATH} ---")


# --- Main ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate MuQ Models or Generate Embeddings")
    parser.add_argument('--task', type=str, default='evaluate', choices=['evaluate', 'generate_embeddings'],
                        help="Task to perform.")
    parser.add_argument('--model_path', type=str, default=DEFAULT_FINETUNED_MODEL_PATH,
                        help="Path to the model file for embedding generation.")
    parser.add_argument('--output_dir', type=str, default=FINETUNED_MUQ_EMBEDDING_DIR,
                        help="Directory to save generated embeddings.")

    args = parser.parse_args()

    if args.task == 'evaluate':
        evaluate_models()
    elif args.task == 'generate_embeddings':
        generate_embeddings(args.model_path, args.output_dir)
    else:
        print(f"Invalid task '{args.task}'. Please choose from the available choices.")

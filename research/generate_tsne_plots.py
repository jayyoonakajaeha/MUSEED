import torch
import numpy as np
import os
import json
import argparse
from tqdm import tqdm
from collections import defaultdict
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Set font for Korean support if available, otherwise default
# plt.rcParams['font.family'] = 'NanumSquareNeo' 

def load_embeddings_and_labels(embedding_dir, jsonl_path, axes_to_evaluate):
    print(f"\nLoading metadata from {jsonl_path}...")
    track_metadata = {}
    
    with open(jsonl_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                track_id = str(data['track_id'])
                meta_flat = {}
                for axis in axes_to_evaluate:
                    val = data.get(axis)
                    if val is None:
                        if axis == 'source':
                            val = data.get('instrumentation', {}).get('source')
                        elif axis in ['valence', 'energy']:
                            val = data.get('affect', {}).get(axis)
                    meta_flat[axis] = val
                track_metadata[track_id] = meta_flat
            except:
                continue

    print(f"Loading embeddings from {embedding_dir}...")
    embeddings = []
    labels = defaultdict(list)
    track_ids = []
    
    files = [f for f in os.listdir(embedding_dir) if f.endswith('.npy')]
    
    for filename in tqdm(files, desc="Matching"):
        track_id_str = os.path.splitext(filename)[0]
        if track_id_str in track_metadata:
            try:
                emb = np.load(os.path.join(embedding_dir, filename))
                if emb.ndim > 1: emb = emb.mean(axis=0)
                embeddings.append(emb)
                track_ids.append(track_id_str)
                meta = track_metadata[track_id_str]
                for axis in axes_to_evaluate:
                    labels[axis].append(meta.get(axis))
            except: pass

    return np.array(embeddings), dict(labels)

def main(args):
    AXES_TO_EVALUATE = ['genre', 'source', 'valence', 'energy', 'mood_style']
    X, y_all_axes = load_embeddings_and_labels(args.embedding_dir, args.jsonl_path, AXES_TO_EVALUATE)
    model_name = args.model_name
    results = {}

    print("\n--- Generating t-SNE Visualization (All Axes) ---")
    
    for axis in AXES_TO_EVALUATE:
        print(f"  - Generating t-SNE for axis: {axis}")
        axis_labels = np.array(y_all_axes[axis])
        valid_indices_axis = [i for i, label in enumerate(axis_labels) if label is not None]
        
        if not valid_indices_axis:
            print(f"    No valid labels found for axis '{axis}'. Skipping t-SNE.")
            continue
        X_axis = X[valid_indices_axis]
        y_axis = axis_labels[valid_indices_axis]
        
        # Data Splitting for Linear Probe (Required for user's snippet variables)
        le = LabelEncoder()
        y_encoded = le.fit_transform(y_axis)
        
        try:
             # Using stratified split as in evaluation
             X_train, X_test, y_train, y_test = train_test_split(
                X_axis, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
        except ValueError:
             # Fallback if stratify fails (rare classes)
             X_train, X_test, y_train, y_test = train_test_split(
                X_axis, y_encoded, test_size=0.2, random_state=42
            )

        # t-SNE 전체 데이터 사용
        tsne_sample_size = len(X_axis)
        X_tsne_sample = X_axis
        y_tsne_sample_labels = y_axis
        
        print(f"    Running t-SNE on {tsne_sample_size} data points for {axis} (Full Dataset)...")
        # 2. Linear Probe (Logistic Regression)
        try:
            # t-SNE 파라미터 튜닝: perplexity 증가, n_iter 증가, init='pca' 사용
            tsne = TSNE(n_components=2, verbose=1, perplexity=50, max_iter=1000, init='pca', learning_rate='auto', random_state=42)
            tsne_results = tsne.fit_transform(X_tsne_sample)
            df_tsne = pd.DataFrame()
            df_tsne['tsne-2d-one'] = tsne_results[:,0]
            df_tsne['tsne-2d-two'] = tsne_results[:,1]
            df_tsne[axis] = y_tsne_sample_labels
            
            # Linear Probe Evaluation
            clf = LogisticRegression(max_iter=1000, n_jobs=-1)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            
            print(f"    Plotting results for {axis}...")
            plt.figure(figsize=(16,10))
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='macro')
            
            # 색상 팔레트 설정 (클래스 수에 따라 조정)
            unique_labels = np.unique(y_tsne_sample_labels)
            n_colors = len(unique_labels)
            palette = sns.color_palette("hsv", n_colors) if n_colors > 10 else sns.color_palette("Set2", n_colors)
            
            sns.scatterplot(
                x="tsne-2d-one", y="tsne-2d-two",
                hue=axis,
                palette=palette,
                data=df_tsne,
                legend="full",
                alpha=0.7
            )
            plt.title(f't-SNE Visualization for {model_name} (colored by {axis.capitalize()})')
            
            # 범례 위치 조정 (너무 많으면 밖으로)
            if n_colors > 15:
                plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            
            plot_filename = f"plots/{model_name}/tsne_{model_name}_{axis}.png"
            os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
            plt.savefig(plot_filename, bbox_inches='tight')
            print(f"    t-SNE plot saved to {plot_filename}")
            plt.close()
            
            results[f'linear_accuracy_{axis}'] = acc
            results[f'linear_macro_f1_{axis}'] = f1
            print(f"Linear Accuracy: {acc:.4f}, Macro-F1: {f1:.4f}")
        except Exception as e:
            print(f"    Error generating t-SNE for {axis}: {e}")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--embedding_dir', required=True)
    parser.add_argument('--jsonl_path', required=True)
    parser.add_argument('--model_name', required=True)
    args = parser.parse_args()
    
    main(args)

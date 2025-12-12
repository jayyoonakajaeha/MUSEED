
import torch
import pandas as pd
import numpy as np
import os
import json
import argparse
from tqdm import tqdm
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, silhouette_score
from sklearn.preprocessing import LabelEncoder
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
# Default Axes to Evaluate
DEFAULT_AXES = ['genre', 'source', 'valence', 'energy', 'mood_style']

def load_embeddings_and_labels(embedding_dir, jsonl_path, axes_to_evaluate):
    """npy 파일 임베딩 로드 및 JSONL 라벨 매칭"""
    print(f"\nLoading metadata from {jsonl_path}...")
    track_metadata = {}
    
    # 1. Load Metadata
    try:
        with open(jsonl_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    track_id = str(data['track_id'])
                    
                    # Normalize metadata structure (Flatten if nested)
                    meta_flat = {}
                    for axis in axes_to_evaluate:
                        val = data.get(axis)
                        if val is None:
                            # 중첩 구조 처리 (예: FMA)
                            if axis == 'source':
                                val = data.get('instrumentation', {}).get('source')
                            elif axis in ['valence', 'energy']:
                                val = data.get('affect', {}).get(axis)
                        meta_flat[axis] = val
                    
                    track_metadata[track_id] = meta_flat
                except:
                    continue
    except FileNotFoundError:
        print(f"Error: JSONL file not found at {jsonl_path}")
        return None, None, None

    print(f"Loaded metadata for {len(track_metadata)} tracks.")

    # 2. Load Embeddings
    print(f"Loading embeddings from {embedding_dir}...")
    embeddings = []
    labels = defaultdict(list)
    track_ids = []
    
    if not os.path.exists(embedding_dir):
        print(f"Error: Embedding directory not found at {embedding_dir}")
        return None, None, None

    files = [f for f in os.listdir(embedding_dir) if f.endswith('.npy')]
    
    for filename in tqdm(files, desc="Matching embeddings"):
        track_id_str = os.path.splitext(filename)[0]
        
        if track_id_str in track_metadata:
            try:
                emb = np.load(os.path.join(embedding_dir, filename))
                if emb.ndim == 1:
                    embeddings.append(emb)
                    track_ids.append(track_id_str)
                    
                    # Add labels
                    meta = track_metadata[track_id_str]
                    for axis in axes_to_evaluate:
                        labels[axis].append(meta.get(axis))
            except:
                pass

    if not embeddings:
        print("No valid embeddings found matching metadata.")
        return None, None, None

    return np.array(embeddings), dict(labels), track_ids

def run_evaluation(embedding_dir, jsonl_path, model_name, axes=DEFAULT_AXES, output_json="results/evaluation_results.json"):
    print(f"\n{'='*20} Evaluating Model: {model_name} {'='*20}")
    
    X, y_dict, _ = load_embeddings_and_labels(embedding_dir, jsonl_path, axes)
    if X is None:
        return

    results = {'model_name': model_name}

    for axis in axes:
        print(f"\n--- Evaluating Axis: {axis} ---")
        y = np.array(y_dict[axis])
        
        # None 제거
        valid_mask = y != None
        X_axis = X[valid_mask]
        y_axis = y[valid_mask]
        
        # 희귀 클래스 필터링 (<2 샘플)
        unique, counts = np.unique(y_axis, return_counts=True)
        valid_classes = unique[counts >= 2]
        mask_class = np.isin(y_axis, valid_classes)
        
        X_axis = X_axis[mask_class]
        y_axis = y_axis[mask_class]
        
        if len(X_axis) < 10:
            print(f"Skipping {axis}: Not enough data.")
            continue

        # 라벨 인코딩
        le = LabelEncoder()
        y_encoded = le.fit_transform(y_axis)
        
        # 데이터 분할
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X_axis, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
        except ValueError:
            print(f"Skipping {axis}: 계층적 분할 불가 (클래스 불균형 심함).")
            continue

        # 1. KNN
        try:
            knn = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
            knn.fit(X_train, y_train)
            y_pred = knn.predict(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='macro')
            
            results[f'knn_accuracy_{axis}'] = acc
            results[f'knn_macro_f1_{axis}'] = f1
            print(f"KNN Accuracy: {acc:.4f}, Macro-F1: {f1:.4f}")
        except Exception as e:
            print(f"KNN Error: {e}")

        # 2. Linear Probe (Logistic Regression)
        try:
            clf = LogisticRegression(max_iter=1000, n_jobs=-1)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='macro')
            
            results[f'linear_accuracy_{axis}'] = acc
            results[f'linear_macro_f1_{axis}'] = f1
            print(f"Linear Accuracy: {acc:.4f}, Macro-F1: {f1:.4f}")
        except Exception as e:
            print(f"Linear Error: {e}")
            
    # 결과 저장
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    all_results = []
    if os.path.exists(output_json):
        try:
            with open(output_json, 'r') as f:
                all_results = json.load(f)
        except: pass
    
    # 모델명 일치 시 기존 결과 업데이트
    updated = False
    for i, res in enumerate(all_results):
        if res.get('model_name') == model_name:
            all_results[i] = results
            updated = True
            break
    if not updated:
        all_results.append(results)
        
    with open(output_json, 'w') as f:
        json.dump(all_results, f, indent=4)
        
    print(f"\nResults saved to {output_json}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate embeddings against ground truth metadata')
    parser.add_argument('--embedding_dir', type=str, required=True, help='Directory containing .npy embeddings')
    parser.add_argument('--jsonl_path', type=str, required=True, help='Path to metadata.jsonl')
    parser.add_argument('--model_name', type=str, required=True, help='Name for this evaluation run')
    parser.add_argument('--output_json', type=str, default='results/evaluation_results.json', help='Path to save results JSON')
    
    args = parser.parse_args()
    
    run_evaluation(args.embedding_dir, args.jsonl_path, args.model_name, output_json=args.output_json)
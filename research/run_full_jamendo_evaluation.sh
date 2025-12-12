#!/bin/bash
set -e

# Model Paths
TRIPLET_MODEL="/home/jay/MusicAI/MUSEED/models/muq_finetuned_triplet_float32_v1(real).pth"
CONTRASTIVE_V1="/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v1.pth"
CONTRASTIVE_V2="/home/jay/MusicAI/MUSEED/models/muq_contrastive_simclr_v2.pth"

# Embedding Dirs
MULAN_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_mulan_v2"
TRIPLET_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_triplet"
CONTRASTIVE_V1_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_contrastive_v1"
CONTRASTIVE_V2_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_contrastive_v2"
BASE_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_base_muq"

PYTHON="/home/jay/EMAs/gate/mambaforge/envs/MuQ/bin/python3"

echo "=== Starting Full Jamendo Evaluation ==="

# 1. Generate Embeddings (using robust script)
# MuQ-MuLan
echo "Generating MuQ-MuLan Embeddings..."
$PYTHON research/generate_embeddings_robust.py \
    --model_path muq-mulan \
    --output_dir $MULAN_EMB_DIR

# Triplet
echo "Generating Triplet Embeddings..."
$PYTHON research/generate_embeddings_robust.py \
    --model_path "$TRIPLET_MODEL" \
    --output_dir $TRIPLET_EMB_DIR

# Contrastive V1
echo "Generating Contrastive V1 Embeddings..."
$PYTHON research/generate_embeddings_robust.py \
    --model_path "$CONTRASTIVE_V1" \
    --output_dir $CONTRASTIVE_V1_EMB_DIR

# Contrastive V2
echo "Generating Contrastive V2 Embeddings..."
$PYTHON research/generate_embeddings_robust.py \
    --model_path "$CONTRASTIVE_V2" \
    --output_dir $CONTRASTIVE_V2_EMB_DIR


# 2. Evaluate All Models
echo "=== Running Evaluations ==="

# Base
echo "Evaluating Base MuQ..."
$PYTHON research/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type base \
  --base_model_name "Base_MuQ_Jamendo_MultiAxis" \
  --embedding_dir_override $BASE_EMB_DIR

# MuLan
echo "Evaluating MuLan..."
$PYTHON research/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type base \
  --base_model_name "MuQ_MuLan_Jamendo" \
  --embedding_dir_override $MULAN_EMB_DIR

# Triplet
echo "Evaluating Triplet..."
$PYTHON research/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type finetuned \
  --finetuned_model_name "Triplet_MuQ_Jamendo" \
  --embedding_dir_override $TRIPLET_EMB_DIR

# Contrastive V1
echo "Evaluating Contrastive V1..."
$PYTHON research/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type finetuned \
  --finetuned_model_name "Contrastive_V1_Jamendo" \
  --embedding_dir_override $CONTRASTIVE_V1_EMB_DIR

# Contrastive V2
echo "Evaluating Contrastive V2..."
$PYTHON research/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type finetuned \
  --finetuned_model_name "Contrastive_V2_Jamendo" \
  --embedding_dir_override $CONTRASTIVE_V2_EMB_DIR

echo "=== All Done ==="

#!/bin/bash
set -e
PYTHON="/home/jay/EMAs/gate/mambaforge/envs/MuQ/bin/python3"

# Embedding Dirs
MULAN_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_mulan_v2"
TRIPLET_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_triplet"
CONTRASTIVE_V1_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_contrastive_v1"
CONTRASTIVE_V2_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_contrastive_v2"
BASE_EMB_DIR="/home/jay/MusicAI/jamendo_embeddings_base_muq"

echo "=== Running Evaluations Only ==="

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

echo "=== Evaluations Done ==="

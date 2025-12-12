#!/bin/bash
set -e

PYTHON_EXEC="/home/jay/EMAs/gate/mambaforge/envs/MuQ/bin/python3"
RESEARCH_DIR="/home/jay/MusicAI/MUSEED/research"
MODEL_PATH="/home/jay/MusicAI/MUSEED/models/muq_finetuned_triplet_float32_v1(real).pth"
OUTPUT_DIR="/home/jay/MusicAI/jamendo_embeddings_finetuned_v3/"

echo ">>> Step 1: Generating Embeddings for Jamendo..."
$PYTHON_EXEC $RESEARCH_DIR/evaluate_model.py \
  --task generate_embeddings \
  --dataset jamendo \
  --model_path "$MODEL_PATH" \
  --output_dir "$OUTPUT_DIR" \
  --batch_size 64 \
  --parallel_processes 1 \
  --num_workers 0

echo ">>> Step 2: Evaluating Models on Jamendo..."
$PYTHON_EXEC $RESEARCH_DIR/evaluate_model.py \
  --task evaluate \
  --dataset jamendo \
  --model_type both \
  --finetuned_model_name "FineTuned_Triplet_v1"

echo ">>> All done!"

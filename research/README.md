# MUSEED Research & AI Scripts / MUSEED 연구 및 AI 스크립트

This directory contains the Python scripts used for data analysis, model training, and evaluation.

이 디렉토리에는 데이터 분석, 모델 학습 및 평가에 사용되는 Python 스크립트들이 포함되어 있습니다.

---

## English

### Key Scripts

#### Data Processing
- `analyze_from_embeddings.py`: Generates multi-axis tags (genre, mood, energy, etc.) from audio embeddings.
- `extract_embeddings.py`: Extracts raw embeddings from audio files using the MuQ model.
- `fma_triplet_dataset.py`: PyTorch Dataset class for loading triplets (Anchor, Positive, Negative) for training.
- `prepare_jamendo_dataset.py`: Prepares Jamendo dataset metadata.

#### Training
- `train_contrastive.py`: SimCLR-based Contrastive Learning (V2 available).
- `train_triplet_loss.py`: Fine-tuning MuQ using Triplet Loss.

#### Evaluation
- `evaluate_model.py`: Evaluates the model using KNN accuracy, Silhouette Score, and generates t-SNE plots.

---

## 한국어 (Korean)

### 주요 스크립트

#### 데이터 처리 (Data Processing)
- `analyze_from_embeddings.py`: 오디오 임베딩으로부터 다축 태그(장르, 분위기, 에너지 등)를 생성합니다.
- `extract_embeddings.py`: MuQ 모델을 사용하여 오디오 파일에서 원시 임베딩을 추출합니다.
- `fma_triplet_dataset.py`: 학습을 위한 삼중항(앵커, 긍정, 부정) 데이터를 로드하는 PyTorch Dataset 클래스입니다.
- `prepare_jamendo_dataset.py`: Jamendo 데이터셋 메타데이터를 준비합니다.

#### 학습 (Training)
- `train_contrastive.py`: SimCLR 기반 대조 학습 스크립트입니다.
- `train_triplet_loss.py`: Triplet Loss를 사용하여 MuQ 모델을 파인튜닝하는 스크립트입니다.

#### 평가 (Evaluation)
- `evaluate_model.py`: KNN 정확도, 실루엣 스코어 등으로 모델을 평가하고 t-SNE 시각화 그래프를 생성합니다.

### 결과물 (Results)
- `results/`: 평가 지표 및 생성된 태그가 담긴 JSON/JSONL 파일들이 저장됩니다.
- `plots/`: t-SNE 그래프 등 시각화 이미지가 저장됩니다.

---

### Setup & Usage (설정 및 사용법)

#### 1. Environment Setup (환경 설정)
It is recommended to use Conda/Mamba to create a virtual environment.

Conda/Mamba를 사용하여 가상 환경을 생성하는 것을 권장합니다.

```bash
# Create and activate environment
mamba create -n MuQ python=3.10
mamba activate MuQ

# Install dependencies
pip install -r requirements.txt
```

#### 2. Training (학습)
To train the model (e.g., Contrastive Learning), run:

모델 학습(예: Contrastive Learning)을 위해 다음 명령어를 실행합니다:

```bash
# Ensure you are in the research directory
cd research

# Run training script
python train_contrastive.py
```

**Note:** You might need to adjust `JSONL_PATH` or data directories in the script or via environment variables.

**참고:** 스크립트 내의 `JSONL_PATH`나 데이터 디렉토리 경로를 수정하거나 환경 변수로 설정해야 할 수 있습니다.

#### 3. Evaluation (평가)
To evaluate the trained model:

학습된 모델을 평가하려면:

```bash
python evaluate_model.py
```
---
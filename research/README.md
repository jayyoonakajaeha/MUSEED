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
- `train_triplet_loss.py`: Triplet Loss를 사용하여 MuQ 모델을 파인튜닝하는 스크립트입니다.

#### 평가 (Evaluation)
- `evaluate_model.py`: KNN 정확도, 실루엣 스코어 등으로 모델을 평가하고 t-SNE 시각화 그래프를 생성합니다.

### 결과물 (Results)
- `results/`: 평가 지표 및 생성된 태그가 담긴 JSON/JSONL 파일들이 저장됩니다.
- `plots/`: t-SNE 그래프 등 시각화 이미지가 저장됩니다.

### 사용법 (Usage)
스크립트를 실행하기 전에 올바른 가상 환경(예: `MuQ`)이 활성화되어 있고 의존성 패키지들이 설치되어 있는지 확인하세요. 스크립트 내의 파일 경로들을 로컬 데이터 디렉토리에 맞게 수정해야 할 수도 있습니다.
# MUSEED Research & AI Scripts / MUSEED 연구 및 AI 스크립트

This directory contains the Python scripts used for data analysis, model training, evaluation, and visualization.
이 디렉토리에는 데이터 분석, 모델 학습, 평가 및 시각화에 사용되는 Python 스크립트들이 포함되어 있습니다.

---

## English

### Key Scripts

#### 1. Data Preparation (데이터 준비)
- **`prepare_jamendo_dataset.py`**: Downloads Jamendo dataset and prepares metadata.
  - Output: `../../jamendo_formatted` (Sibling directory).
- **`preprocess_fma_genres.py`**: Pre-processes FMA metadata (requires FMA data in `../../fma`).
- **`split_dataset.py`**: Splits the analyzed data into Train/Test sets.
- **`build_faiss_index.py`**: Builds the FAISS index from generated embeddings for the backend.
- **`extract_embeddings_mean_pooling.py`**: Extracts mean-pooled embeddings from audio files using MuQ (Recommended).
- **`extract_embeddings.py`**: Legacy script for raw embedding extraction.

#### 2. Training (학습)
- **`train_contrastive.py`**: SimCLR-based Contrastive Learning (V2 available).
- **`train_triplet_loss.py`**: Fine-tuning MuQ using Triplet Loss with Hard Negative Mining.

#### 3. Evaluation & Analysis (평가 및 분석)
- **`evaluate_model.py`**: Evaluates the model using KNN accuracy, Silhouette Score, and generates t-SNE plots.
- **`generate_tsne_plots.py`**: Generates t-SNE visualization plots for different axes (Genre, Energy, Mood).
- **`analyze_from_embeddings.py`**: Generates multi-axis tags (genre, mood, energy) from audio embeddings.

---

## 한국어 (Korean)

### 주요 스크립트

#### 1. 데이터 준비 (Data Preparation)
- **`prepare_jamendo_dataset.py`**: Jamendo 데이터셋 다운로드 및 메타데이터 준비 (결과물: `../../jamendo_formatted`).
- **`preprocess_fma_genres.py`**: FMA 메타데이터 전처리 (`../../fma` 경로 필요).
- **`split_dataset.py`**: 데이터셋을 학습/테스트 셋으로 분할합니다.
- **`build_faiss_index.py`**: 생성된 임베딩으로 백엔드 검색용 FAISS 인덱스를 생성합니다.
- **`extract_embeddings_mean_pooling.py`**: 오디오 파일에서 평균 풀링(Mean Pooling)된 임베딩을 추출합니다 (권장).
- **`extract_embeddings.py`**: (구버전) 원시 임베딩 추출 스크립트.

#### 2. 학습 (Training)
- **`train_contrastive.py`**: SimCLR 기반 대조 학습 스크립트입니다.
- **`train_triplet_loss.py`**: Hard Negative Mining을 포함한 Triplet Loss 파인튜닝 스크립트입니다.

#### 3. 평가 및 분석 (Evaluation & Analysis)
- **`evaluate_model.py`**: KNN 정확도, 실루엣 스코어 등으로 모델을 평가합니다.
- **`generate_tsne_plots.py`**: 장르, 에너지, 무드 등 다양한 축에 대한 t-SNE 시각화 그래프를 생성합니다.
- **`analyze_from_embeddings.py`**: 오디오 임베딩으로부터 다축 태그(장르, 분위기, 에너지 등)를 분석 및 생성합니다.

---

### Setup & Usage

Refer to the main **`../README.md`** for detailed usage instructions and environment setup.
자세한 사용법 및 환경 설정은 메인 **`../README.md`**를 참고하세요.
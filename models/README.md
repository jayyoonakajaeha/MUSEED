# MUSEED Models / MUSEED 모델

This folder stores the model checkpoints and weights.

이 폴더는 모델의 체크포인트와 가중치 파일을 저장하는 곳입니다.

---

## English

### MuQ Model
The core of our recommendation engine is based on the MuQ model.

1. **Base Model:** `MuQ-large-msd-iter` (Pre-trained)
2. **Fine-tuned Models:**
    - `muq_contrastive_simclr_v2.pth`: SimCLR-based Contrastive Learning model (Used for Embeddings).
    - `muq_finetuned_triplet_float32_v1.pth`: Triplet Loss fine-tuned model.

### FAISS Index
- `faiss_index.bin`: The vector search index built from `embeddings/`.
- `faiss_track_ids.json`: Mapping from FAISS index IDs to Track IDs.

### Download
If you are setting this up from scratch, you will need to:
1. Train the model using the scripts in `../research/`.
2. Or place your provided `.pth` and index files here.

---

## 한국어 (Korean)

### MuQ 모델
MUSEED 추천 엔진의 핵심은 MuQ 모델을 기반으로 합니다.

1. **기본 모델 (Base Model):** `MuQ-large-msd-iter`
2. **파인튜닝 모델 (Fine-tuned Models):**
    - `muq_contrastive_simclr_v2.pth`: SimCLR 기반 대조 학습 모델 (임베딩 추출용).
    - `muq_finetuned_triplet_float32_v1.pth`: Triplet Loss 파인튜닝 모델.

### FAISS 인덱스
- `faiss_index.bin`: `embeddings/` 데이터를 기반으로 구축된 벡터 검색 인덱스입니다.
- `faiss_track_ids.json`: FAISS 인덱스 ID와 트랙 ID 간의 매핑 파일입니다.

### 다운로드
이 프로젝트를 처음부터 설정하는 경우:
1. `../research/` 폴더의 스크립트를 사용하여 직접 학습시킵니다.
2. 또는 제공된 `.pth` 및 인덱스 파일을 이곳에 위치시킵니다.
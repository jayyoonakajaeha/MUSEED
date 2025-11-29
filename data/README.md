# MUSEED Datasets / MUSEED 데이터셋

This folder is intended to store the large datasets required for training and evaluating the MUSEED models. Due to file size limits, the actual data is not included in this repository.

이 폴더는 MUSEED 모델 학습 및 평가에 필요한 대용량 데이터셋을 저장하기 위한 곳입니다. 파일 크기 제한으로 인해 실제 데이터는 이 저장소에 포함되어 있지 않습니다.

---

## English

### Required Datasets

#### 1. Free Music Archive (FMA)
- **Description:** A large-scale dataset for music analysis.
- **Download:** You can download the dataset from the [official FMA repository](https://github.com/mdeff/fma).
- **Setup:**
  - Extract the `fma_full` or `fma_large` dataset into a folder named `fma` within this directory or link it appropriately in the configuration scripts.
  - Expected path: `./fma/data/fma_full`

#### 2. Pre-computed Embeddings
To speed up training, we use pre-computed embeddings from the MuQ model.
- **Folders to create:**
  - `fma_audio_embeddings_base_muq/`: Embeddings from the base MuQ model.
  - `fma_audio_embeddings_finetuned_muq_v3/`: Embeddings from the fine-tuned model.
  - `track_embeddings/`: Intermediate embeddings.

## File Structure
After downloading, your data directory structure should look like this (conceptually):

```
data/
├── fma/
│   ├── data/
│   │   ├── fma_full/
│   │   └── fma_metadata/
├── fma_audio_embeddings_base_muq/
└── ...
```

---

## 한국어 (Korean)

### 필수 데이터셋

#### 1. Free Music Archive (FMA)
- **설명:** 음악 분석을 위한 대규모 데이터셋입니다.
- **다운로드:** [공식 FMA 저장소](https://github.com/mdeff/fma)에서 데이터셋을 다운로드할 수 있습니다.
- **설치 방법:**
  - `fma_full` 또는 `fma_large` 데이터셋의 압축을 풀어 이 디렉토리 내에 `fma`라는 이름의 폴더로 저장하거나, 설정 스크립트에서 해당 경로를 연결해 주세요.
  - 예상 경로: `./fma/data/fma_full`

#### 2. 사전 계산된 임베딩 (Pre-computed Embeddings)
학습 속도를 높이기 위해 MuQ 모델에서 미리 추출한 임베딩을 사용합니다.
- **생성해야 할 폴더:**
  - `fma_audio_embeddings_base_muq/`: 기본 MuQ 모델에서 추출한 임베딩.
  - `fma_audio_embeddings_finetuned_muq_v3/`: 파인튜닝된 모델에서 추출한 임베딩.
  - `track_embeddings/`: 중간 단계 임베딩.

## 파일 구조
다운로드 후 데이터 디렉토리 구조는 대략 다음과 같아야 합니다:

```
data/
├── fma/
│   ├── data/
│   │   ├── fma_full/
│   │   └── fma_metadata/
├── fma_audio_embeddings_base_muq/
└── ...
```
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

#### 2. Pre-computed Embeddings (사전 계산된 임베딩)
To speed up training and inference, we use pre-computed embeddings.
학습 및 추론 속도를 높이기 위해 사전 계산된 임베딩을 사용합니다.

- **Generated Folders (생성되는 폴더):**
  - `embeddings/`: Consolidated embeddings for serving (Train/Test/Jamendo). (서비스용 통합 임베딩)
  - `embeddings_contrastive_v2_mean/`: Mean-pooled embeddings from the Contrastive V2 model. (Contrastive V2 모델의 평균 풀링 임베딩)

## File Structure (파일 구조)
The directory structure should look like this:
디렉토리 구조는 다음과 같습니다:

```
data/
├── fma/
│   ├── data/
│   │   ├── fma_full/
│   │   └── fma_metadata/
├── embeddings/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
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
학습 및 추론 속도를 높이기 위해 사전 계산된 임베딩을 사용합니다.

- **생성해야 할 폴더:**
  - `embeddings/`: 서비스용 통합 임베딩 (Train/Test/Jamendo).
  - `embeddings_contrastive_v2_mean/`: Contrastive V2 모델의 평균 풀링 임베딩.

## 파일 구조
디렉토리 구조는 다음과 같습니다:

```
data/
├── fma/
│   ├── data/
│   │   ├── fma_full/
│   │   └── fma_metadata/
├── embeddings/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
```
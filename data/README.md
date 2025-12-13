# MUSEED Datasets / MUSEED 데이터셋

This folder is intended to store the processed **Metadata and Embeddings** for MUSEED.
Note: The **Raw Audio Files** (FMA, Jamendo) are stored in **Sibling Directories** outside of this project folder.

이 폴더는 MUSEED의 **메타데이터 및 임베딩**을 저장하는 공간입니다.
주의: **원본 오디오 파일**(FMA, Jamendo)은 이 프로젝트 폴더 외부의 **형제 디렉토리**에 저장됩니다.

---

## English

### Required Datasets

#### 1. Free Music Archive (FMA)
- **Location:** Sibling Directory (`../../fma`)
- **Setup:**
  - Extract the `fma_full` or `fma_large` dataset into a **sibling directory** named `fma`.
  - Expected path: `../../fma/data/fma_full`

#### 2. Pre-computed Embeddings (사전 계산된 임베딩)
To speed up training and inference, we use pre-computed embeddings stored in this folder.
학습 및 추론 속도를 높이기 위해 이 폴더에 저장된 사전 계산된 임베딩을 사용합니다.

- **Generated Folders (생성되는 폴더):**
  - `embeddings/`: Consolidated embeddings for serving (Train/Test/Jamendo). (서비스용 통합 임베딩)
  - `embeddings_contrastive_v2_mean/`: Mean-pooled embeddings from the Contrastive V2 model. (Contrastive V2 모델의 평균 풀링 임베딩)
  - `embeddings_jamendo/`: Embeddings for Jamendo tracks.

## File Structure (파일 구조)
The directory structure should look like this:
디렉토리 구조는 다음과 같습니다:

```
data/
├── embeddings/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
```

(Note: `fma/` folder is NOT here. It is at `../../fma/`)

---

## 한국어 (Korean)

### 필수 데이터셋

#### 1. Free Music Archive (FMA)
- **위치:** 형제 디렉토리 (`../../fma`)
- **설치 방법:**
  - `fma_full` 또는 `fma_large` 데이터셋의 압축을 풀어 **형제 디렉토리**인 `../../fma`에 저장해 주세요.
  - 예상 경로: `../../fma/data/fma_full`

#### 2. 사전 계산된 임베딩 (Pre-computed Embeddings)
학습 및 추론 속도를 높이기 위해 이 폴더에 저장된 사전 계산된 임베딩을 사용합니다.

- **생성해야 할 폴더:**
  - `embeddings/`: 서비스용 통합 임베딩 (Train/Test/Jamendo).
  - `embeddings_contrastive_v2_mean/`: Contrastive V2 모델의 평균 풀링 임베딩.

## 파일 구조
디렉토리 구조는 다음과 같습니다:

```
data/
├── embeddings/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
```
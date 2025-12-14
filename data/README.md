# MUSEED Datasets / MUSEED 데이터셋

This folder is intended to store the processed **Metadata and Embeddings** for MUSEED.
Note: The **Raw Audio Files** (FMA, Jamendo) are stored in **Sibling Directories** outside of this project folder.

이 폴더는 MUSEED의 **메타데이터 및 임베딩**을 저장하는 공간입니다.
주의: **원본 오디오 파일**(FMA, Jamendo)은 이 프로젝트 폴더 외부의 **형제 디렉토리**에 저장됩니다.

---
## 한국어 (Korean)

### 필수 데이터셋

#### 1. Free Music Archive (FMA)
- **위치:** 형제 디렉토리 (`../../fma`)
- **설치 방법:**
  - `fma_full` 또는 `fma_large` 데이터셋의 압축을 풀어 **형제 디렉토리**인 `../../fma`에 저장해 주세요.
  - 예상 경로: `../../fma/data/fma_full`

#### 2. 사전 계산된 임베딩 (Pre-computed Embeddings)
학습 및 추론 속도를 높이기 위해 이 폴더에 저장된 사전 계산된 임베딩을 사용합니다. 다음 두 가지 방법 중 하나를 선택할 수 있습니다.

**옵션 A: 다운로드하여 사용 (권장)**
> [!TIP]
> **다운로드 (Download):** [Google Drive Link](https://drive.google.com/drive/folders/19mu28UKnuDsZ6-k6ebbQBz29_g6s9Xtw?usp=sharing)
> 위 링크에서 `embeddings_contrastive_v2_mean.zip` 및 메타데이터 파일들을 다운로드하여 이곳에 압축을 풀어주세요.

**옵션 B: 직접 생성**
제공된 스크립트를 실행하여 직접 임베딩을 추출할 수도 있습니다.

- **최종적으로 위치해야 할 폴더:**
  - `embeddings_contrastive_v2_mean/`: Contrastive V2 모델의 평균 풀링 임베딩.

## 파일 구조
디렉토리 구조는 다음과 같습니다:

```
data/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
```
---

## English

### Required Datasets

#### 1. Free Music Archive (FMA)
- **Location:** Sibling Directory (`../../fma`)
- **Setup:**
  - Extract the `fma_full` or `fma_large` dataset into a **sibling directory** named `fma`.
  - Expected path: `../../fma/data/fma_full`

#### 2. Pre-computed Embeddings
To speed up training and inference, we use pre-computed embeddings stored in this folder. You can choose one of the two options below.

**Option A: Download (Recommended)**
> [!TIP]
> **Download:** [Google Drive Link](https://drive.google.com/drive/folders/19mu28UKnuDsZ6-k6ebbQBz29_g6s9Xtw?usp=sharing)
> Download `embeddings_contrastive_v2_mean.zip` and metadata files from the link above and unzip them here.

**Option B: Generate Yourself**
You can also run the provided scripts to extract embeddings yourself.

- **Final Folder Location:**
  - `embeddings_contrastive_v2_mean/`: Mean-pooled embeddings from the Contrastive V2 model.

## File Structure
The directory structure should look like this:

```
data/
├── embeddings_contrastive_v2_mean/
├── train_metadata.jsonl
├── test_metadata.jsonl
├── jamendo_rich_metadata.jsonl
└── multi_axis_analysis_results.jsonl
```

(Note: `fma/` folder is NOT here. It is at `../../fma/`)


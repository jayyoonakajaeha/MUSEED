# MUSEED Models / MUSEED 모델

This folder stores the model checkpoints and weights.

이 폴더는 모델의 체크포인트와 가중치 파일을 저장하는 곳입니다.

---

## English

### MuQ Model
The core of our recommendation engine is based on the MuQ model.

- **Base Model:** We use the pre-trained `MuQ-large-msd-iter` model.
- **Fine-tuned Model:** The model is fine-tuned using Triplet Loss on the FMA dataset.

### Checkpoints
Place your `.pth` model files here.

- `muq_finetuned_triplet_float32_v3.pth`: The latest fine-tuned checkpoint used for the final evaluation.

### Download
If you are setting this up from scratch, you will need to either:
1. Train the model using the scripts in `../research/`.
2. Download the pre-trained weights from external storage (link to be added).

---

## 한국어 (Korean)

### MuQ 모델
MUSEED 추천 엔진의 핵심은 MuQ 모델을 기반으로 합니다.

- **기본 모델 (Base Model):** 사전 학습된 `MuQ-large-msd-iter` 모델을 사용합니다.
- **파인튜닝 모델 (Fine-tuned Model):** FMA 데이터셋을 사용하여 Triplet Loss(삼중항 손실) 방식으로 파인튜닝되었습니다.

### 체크포인트 (Checkpoints)
`.pth` 모델 파일들을 이곳에 위치시켜 주세요.

- `muq_finetuned_triplet_float32_v3.pth`: 최종 평가에 사용된 최신 파인튜닝 체크포인트입니다.

### 다운로드
이 프로젝트를 처음부터 설정하는 경우 다음 중 하나를 수행해야 합니다:
1. `../research/` 폴더에 있는 스크립트를 사용하여 모델을 직접 학습시킵니다.
2. 외부 저장소(링크 추가 예정)에서 사전 학습된 가중치를 다운로드합니다.
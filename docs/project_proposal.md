# "시드 음악 한 곡으로, 취향저격 AI 플레이리스트 완성" - MUSEED 개발 제안서

본 제안서는 사용자가 좋아하는 '시드(Seed) 음악' 한 곡을 입력하면, AI가 해당 곡의 장르, 분위기, 악기 구성까지 심층 분석하여 사용자의 숨겨진 취향까지 찾아내는 개인 맞춤형 플레이리스트를 자동으로 생성하는 플랫폼, "MUSEED"의 개발을 목표로 합니다. MUSEED는 파인튜닝된 `MuQ` 오디오 인코더와 초고속 벡터 검색 엔진 `Faiss`를 핵심 기술로 활용하여, 단순한 음악 추천을 넘어 새로운 음악을 '발견'하는 즐거움을 제공하고, 비슷한 취향을 가진 사용자들과 음악적 영감을 공유하는 소셜 기능까지 통합한 차세대 뮤직 디스커버리 경험을 제시합니다.

## 1. 프로젝트 개요

### 1.1. 프로젝트명
**MUSEED: AI 플레이리스트 자동 생성 플랫폼**

### 1.2. 핵심 컨셉
**AI 기반의 개인화된 플레이리스트 생성 및 소셜 공유 플랫폼.** 사용자가 제공하는 '시드(Seed) 음악'의 음향적, 감성적 특징을 AI가 심층 분석하여, 취향에 완벽하게 부합하는 새로운 플레이리스트를 자동으로 생성하고, 이를 다른 사용자들과 공유하며 소통하는 차세대 음악 디스커버리 경험을 제공합니다.

### 1.3. 주요 기능
- **AI 기반 플레이리스트 자동 생성**: 사용자가 선택하거나 직접 업로드한 '시드 음악'의 장르, 분위기, 악기 구성 등 다각적인 음향적, 감성적 특징을 AI(파인튜닝된 MuQ 모델)가 심층 분석하여, 시드 음악과 높은 유사도를 가진 곡들로 구성된 개인 맞춤형 플레이리스트를 자동으로 생성합니다.
- **사용자 음원 업로드**: 음원 사이트에 등록되지 않은 사용자 자신의 창작곡, 데모곡 등을 직접 업로드하여 시드 음악으로 활용 가능.
- **소셜 공유 및 인터랙션**:
    - 생성된 플레이리스트를 플랫폼 내에 `Public`으로 게시 및 공유.
    - 다른 사용자의 플레이리스트를 감상하고 '좋아요'를 누르거나 자신의 계정에 저장.
    - 취향이 비슷한 다른 사용자를 '팔로우'하고 소통.
- **게이미피케이션 및 프로필 커스터마이징**:
    - 활동(플레이리스트 생성, '좋아요' 획득 등)에 따라 '배지' 획득.
    - 사용자가 생성한 플레이리스트의 장르 비율을 원형 그래프로 시각화.
    - 장르 비율에 따라 사용자의 프로필 아바타가 자동으로 꾸며지는 기능.

### 1.4. 차별점 및 기대효과
- **데이터 없이 시작하는 정교한 개인화 (Cold-Start 문제 해결)**: 대부분의 추천 시스템이 사용자 데이터 축적을 필요로 하는 반면, MUSEED는 음악 자체의 음향적, 감성적 특징을 심층 분석하는 콘텐츠 기반 AI 모델을 사용합니다. 따라서 신규 사용자라도 **시드 음악 단 한 곡만으로 즉시 정교하고 만족도 높은 개인 맞춤형 플레이리스트를 제공**받을 수 있습니다.
- **창작자를 위한 AI 기반 레퍼런스 탐색**: 작곡가, 프로듀서가 자신의 미발매곡과 유사한 무드의 곡을 AI의 정교한 분석을 통해 찾거나, 표절을 피하기 위한 레퍼런스 탐색 도구로 활용.
- **개인화된 새로운 음악 발견 경험**: 기존의 아티스트/앨범 중심의 탐색을 넘어, AI가 분석한 음악의 '분위기'와 '취향'을 중심으로 사용자에게 최적화된 새로운 음악을 발견하는 경험 제공.
- **AI 분석 기반 취향 커뮤니티 형성**: AI의 음악적 유사도 분석을 통해 비슷한 음악적 취향을 가진 사용자들이 자연스럽게 연결되고 소통하는 커뮤니티 활성화.

---

## 2. 프로젝트 구성도

### 2.1. 시스템 아키텍처 (System Architecture)

+----------------------+ +-------------------------+ +-------------------------+ +----------------------------+ +---------------------------+
| Frontend (Web) | | Backend (API) | | Embedding Extractor | | Fine-tuned MuQ Model | | FAISS Search / Database |
| (React / Next.js) |<---->| (Python / FastAPI) |----->| (Python Service) |----->| (PyTorch) |----->| (FAISS / PostgreSQL) |
+----------------------+ +-------------------------+ +-------------------------+ +----------------------------+ +---------------------------+
| - UI/UX Components | | - User Authentication | | - Audio Preprocessing | | - Triplet Loss Fine-tuning | | - Embedding Index Storage |
| - State Management | | - REST API Endpoints | | - Embedding Generation | | - Similarity Scoring | | - Fast Similarity Search |
| - Audio Streaming | | - Business Logic | | (Mel-spec / MuQ Input) | | - Embedding Normalization | | - Metadata Storage (SQL) |
+----------------------+ +-------------------------+ +-------------------------+ +----------------------------+ +---------------------------+


### 2.2. 핵심 기능 흐름도 (Flow Chart: Playlist Generation)
1. **[User]** 로그인 후, “플레이리스트 생성” 버튼 클릭.  
2. **[User]** 오디오 파일을 업로드하거나 기존 DB에서 곡을 선택.  
3. **[Frontend]** 선택된 곡 정보를 백엔드 API `POST /api/playlists`로 전송.  
4. **[Backend]** 요청을 검증 후, 오디오 데이터를 **Embedding Extractor**로 전달.  
5. **[Embedding Extractor]**
   - 입력 오디오를 전처리하고 Mel-spectrogram을 생성.  
   - 파인튜닝된 **MuQ 모델 입력 형식**에 맞게 임베딩 벡터를 추출.  
6. **[Fine-tuned MuQ Model]**
   - Triplet Loss로 학습된 모델이 음악 간 의미적 유사도를 계산.  
   - 시드 곡이 여러 개일 경우, 평균 임베딩을 계산하여 요청 임베딩 생성.  
7. **[FAISS Search]**
   - 전체 임베딩 인덱스에서 요청 임베딩과 가장 유사한 **Top-N 곡**을 빠르게 검색.  
   - 결과 곡 ID 리스트를 백엔드로 반환.  
8. **[Backend]** 곡 ID를 이용해 **PostgreSQL**에서 제목, 아티스트 등 메타데이터 조회.  
9. **[Backend]** 플레이리스트 객체를 생성해 DB에 저장 후, **JSON 형태로 프론트엔드에 반환.**  
10. **[Frontend]** 결과를 화면에 렌더링하고, 사용자는 제목 지정 및 저장/공유 가능.  


---

## 3. 사용할 데이터셋: FMA (Free Music Archive)

본 프로젝트의 기반이 되는 음악 라이브러리와 AI 모델 학습 데이터는 **FMA (Free Music Archive) Dataset**을 활용합니다. FMA는 다양한 장르의 음악을 포함하는 대규모 공개 데이터셋으로, 본 프로젝트의 목적에 가장 부합하는 선택입니다.

- **데이터셋 구성**:
    - **오디오**: `fma_full` 버전에 포함된 **90,192개**의 음원 파일 (`.mp3`) 전체를 사용합니다. 이 음원들은 AI가 최종적으로 사용자에게 추천해 줄 노래의 라이브러리를 구성합니다.
    - **메타데이터**: 트랙 ID, 아티스트, 앨범, 그리고 가장 중요하게는 **장르(genre)** 정보가 포함된 `tracks.csv` 파일을 활용합니다. 특히, 본 프로젝트에서는 16개의 최상위 장르(`track_toplevel_genres`)를 AI 모델의 핵심 학습 특징 및 사용자 프로필 분석 기준으로 사용합니다.

아래는 FMA 데이터셋의 16개 최상위 장르 분포표이며, 'Electronic', 'Experimental', 'Rock' 장르에 데이터가 편중되어 있음을 확인할 수 있습니다. 이 데이터 불균형은 4.2절에서 설명할 '가중 샘플링'을 통해 완화될 것입니다.

| 순위 | 장르 | 트랙 수 |
|:---|:---|:---|
| 1 | Electronic | 21,781 |
| 2 | Experimental | 19,672 |
| 3 | Rock | 17,030 |
| 4 | Pop | 6,812 |
| 5 | Folk | 4,829 |
| 6 | Instrumental | 4,182 |
| 7 | Hip-Hop | 3,891 |
| 8 | International | 2,410 |
| 9 | Jazz | 1,866 |
| 10 | Classical | 1,833 |
| 11 | Blues | 1,538 |
| 12 | Soul-RnB | 799 |
| 13 | Spoken | 550 |
| 14 | Country | 544 |
| 15 | Old-Time / Historic | 344 |
| 16 | Easy Listening | 171 |

- **프로젝트에서의 활용 방안**:
    1.  **유사도 검색 라이브러리 구축**: **90,192개**의 모든 음원에서 `MuQ` 모델을 통해 임베딩 벡터를 추출하고, 이를 `Faiss` 인덱스에 저장하여 AI 플레이리스트 생성을 위한 검색 대상 라이브러리를 구축합니다.
    2.  **모델 파인튜닝을 위한 Triplet 생성**: 1단계에서 생성된 다각도 태그(장르, 무드, 악기 등)와 FMA의 장르 메타데이터를 조합하여, '음악적 유사도'를 학습시키기 위한 `(Anchor, Positive, Negative)` 데이터 삼중항(triplet)을 생성하는 데 사용됩니다. 예를 들어, 같은 'Rock' 장르 내에서도 'Hard Rock'과 'Soft Rock'을 구분하여 학습시키는 등 정교한 데이터셋 구축이 가능합니다.

- **선정 이유**:
    - **규모와 다양성**: 약 9만 곡에 달하는 대규모 데이터와 161개에 달하는 세부 장르 분류는, 다양한 사용자 취향을 만족시킬 수 있는 풍부한 음악 라이브러리를 구축하는 데 이상적입니다.
    - **라이선스**: 연구 및 비상업적 목적으로 자유롭게 사용 가능하여, 본 프로젝트와 같은 학술 및 포트폴리오 개발에 적합합니다.

---

## 4. 데이터 전처리 및 파인튜닝 준비

### 4.1. 1단계: 다각도 태그 생성
- **Workflow**: 2-Step 워크플로우 채택
    1.  **임베딩 추출 (`extract_embeddings.py`)**: FMA 데이터셋의 모든 곡에 대해 사전 학습된 MuQ 모델로 오디오 임베딩을 추출하여, 각 트랙 ID에 해당하는 `.npy` 파일로 영구 저장.
    2.  **태그 분석 (`analyze_from_embeddings.py`)**: 저장된 임베딩을 로드하여, 다양한 텍스트 프롬프트와의 유사도를 계산. 이를 통해 각 곡에 대한 풍부하고 구조화된 JSON 태그를 `multi_axis_analysis_results.jsonl` 파일로 생성.
- **분석 축 (Axes)**:
    - `genre`: 메타데이터 기반의 최상위 장르.
    - `instrumentation`: { `source`: (acoustic/electronic) }
    - `affect`: { `valence`: (positive/negative), `energy`: (high/medium/low) }
    - `mood_style`: 세부 분위기 태그.

### 4.2. 2단계: Triplet 데이터셋 생성
- **규칙 기반 Triplet 생성**: 1단계에서 생성된 다각도 태그를 기반으로, 정교한 규칙을 사용해 `(Anchor, Positive, Negative)` 데이터 삼중항을 생성.
- **장르 불균형 해소를 위한 가중 샘플링 (Weighted Sampling for Genre Imbalance)**: FMA 데이터셋은 'Electronic' 등 특정 장르에 데이터가 편중되어 있습니다. 모델 편향을 방지하기 위해, Triplet의 Anchor 곡을 선택할 때 다음과 같은 **가중 샘플링** 전략을 사용합니다. 각 장르 `i`에 속한 곡의 수를 `N_i`라고 할 때, 해당 장르가 선택될 확률 `P(i)`는 데이터 수의 역수에 비례하도록 설정합니다.
  > P(i) ∝ 1 / N_i
  
  이를 위해, 각 장르의 샘플링 가중치 `w_i = 1 / N_i`를 계산한 뒤, 전체 가중치의 합으로 나누어 최종 샘플링 확률 `p_i = w_i / Σ(w_j)`을 계산하여 적용합니다. 이 전략을 통해 소수 장르에 대한 모델의 이해도를 높이고 전반적인 추천 성능을 안정화합니다.
- **Hard Negative Mining**: 모델이 미묘한 차이를 학습하도록, 실제 분석된 태그를 기반으로 다음과 같이 5단계의 '어려운 네거티브'를 전략적으로 샘플링합니다. 각 단계에서는 '해당 순위의 특징은 다르지만, 그보다 중요한 상위 특징들은 모두 같은' 모든 네거티브를 후보로 삼아, 더 현실적이고 다양한 네거티브를 학습에 활용합니다.
    - **0순위 (Source-Hard)**: `장르`, `감정가`, `분위기`, `에너지`가 모두 동일하지만, **`음색(source)`만 다른 곡**.
    - **1순위 (Energy-Hard)**: `장르`, `감정가`, `분위기`가 동일하면서, **`에너지(energy)`가 다른 곡**. (음색은 달라도 무관)
    - **2순위 (Mood-Hard)**: `장르`, `감정가`가 동일하면서, **`세부 분위기(mood_style)`가 다른 곡**. (에너지, 음색은 달라도 무관)
    - **3순위 (Valence-Hard)**: `장르`가 동일하면서, **`감정가(valence)`가 다른 곡**. (분위기, 에너지, 음색은 달라도 무관)
    - **4순위 (Easy)**: **`장르(genre)` 자체가 다른 곡**.

---

## 5. 핵심 모델 및 기술

### 5.1. 모델 아키텍처 및 역할 분담

본 프로젝트는 두 가지 핵심 모델을 각기 다른 단계에서 전략적으로 활용합니다.

- **태그 생성을 위한 멀티모달 모델: `MuQ-MuLan`**
    - **역할**: 1단계 데이터 전처리 과정에서 FMA 음원의 다각도 태그(장르, 악기, 무드 등)를 생성하는 역할을 담당합니다.
    - **선정 이유**: `MuQ-MuLan`은 오디오와 텍스트를 함께 이해하는(Multi-modal) 모델입니다. "신나는 일렉트로닉 음악"과 같은 텍스트 프롬프트와 오디오 임베딩 간의 유사도 계산이 가능하여, 프로그래밍 방식으로 정교하고 풍부한 태그를 대량 생성하는 데 필수적입니다. 본 프로젝트에서는 사전 학습된 `OpenMuQ/MuQ-MuLan-large` 모델을 그대로 사용합니다.

- **유사도 학습을 위한 오디오 인코더: `MuQ`**
    - **역할**: 2단계에서 Triplet Loss를 사용하여 파인튜닝될 대상 모델입니다.
    - **선정 이유**: `MuQ`는 `MuQ-MuLan`의 오디오 인코더 부분에 해당하는 모델로, 오디오 자체의 음향적 특징을 임베딩 벡터로 추출하는 데 특화되어 있습니다. 1단계에서 생성된 정교한 태그들을 정답지로 활용하여 `MuQ` 모델을 파인튜닝함으로써, '음악적 유사도'를 더 잘 표현하는 임베딩 공간을 학습시키는 것이 목표입니다.

### 5.2. 파인튜닝 방법론: `Triplet Loss`
- **개념**: '기준점(Anchor)'이 되는 데이터에 대해, '유사한 샘플(Positive)'은 임베딩 공간에서 더 가깝게, '유사하지 않은 샘플(Negative)'은 더 멀게 배치하도록 모델을 학습시키는 손실 함수입니다.
- **적용**: 4.2단계에서 생성한 `(Anchor, Positive, Negative)` 데이터 삼중항을 이용해 `MuQ` 모델을 파인튜닝합니다. 이를 통해 모델이 장르, 무드, 악기 구성 등 다각적인 기준의 유사도를 임베딩 벡터 거리로 표현하도록 학습시킵니다. 특히, 'Hard Negative Mining' 전략을 통해 모델이 미묘한 차이를 구분하는 능력을 극대화합니다.

### 5.3. 유사도 검색 엔진: `FAISS`
- **역할**: 최종적으로 파인튜닝된 `MuQ` 모델이 추출한 수만 개의 임베딩 벡터 중에서, 사용자의 시드 음악과 가장 유사한 곡들을 실시간으로 검색하는 역할을 담당합니다.
- **선정 이유**: `FAISS`는 대규모 벡터 데이터셋에서 초고속 유사도 검색(Nearest Neighbor Search)을 지원하는 라이브러리입니다. 이를 통해 수만 곡의 라이브러리 속에서도 지연 없는 플레이리스트 생성이 가능해집니다.

---

## 6. 성능평가 방안

- **정량적 평가 (모델 성능)**
    1.  **k-NN 분류 정확도 비교**: 파인튜닝 전/후 모델의 임베딩을 각각 사용하여, `mood_style` 또는 `genre`에 대한 k-NN 분류 정확도를 측정. 파인튜닝 후 정확도 향상 여부 확인.
    2.  **실루엣 계수 (Silhouette Score) 비교**: 파인튜닝 전/후 임베딩 공간의 장르/분위기별 클러스터링 품질을 실루엣 계수로 측정하여, 군집이 더 명확해졌는지 평가.
    3.  **장르별 성능 분석 (Per-Genre Evaluation)**: 장르 불균형 문제의 해결 여부를 확인하기 위해, **16개 최상위 장르 각각에 대해 k-NN 분류 정확도 및 클러스터링 품질을 개별적으로 측정**합니다. 이를 통해 소수 장르에서도 모델이 안정적인 성능을 보이는지 검증합니다.
    4.  **Triplet Loss 값 모니터링**: 학습 과정에서 Triplet Loss가 안정적으로 감소하는지 확인.
- **정성적 평가 (서비스 품질)**
    1.  **대표 케이스 비교 (Case Study)**: 주류 장르(Rock, Pop)와 **소수 장르(Easy Listening, Spoken) 각각에 대한 시드 곡**으로 플레이리스트를 생성하여, 파인튜닝 전/후 모델의 결과물의 일관성, 의외성, 품질 차이를 심층 분석합니다.
    2.  **t-SNE 시각화**: 파인튜닝 전/후의 임베딩 공간을 2차원으로 시각화하여, 같은 장르나 분위기의 곡들이 더 잘 군집을 형성하는지 직관적으로 확인.

---

## 7. 개발 일정 (8주 기준)

- **1-2주차**:
    - 개발 환경 설정, 데이터셋 준비 및 동기화
    - **1단계: 다각도 태그 생성** 스크립트 (`extract_embeddings.py`, `analyze_from_embeddings.py`) 작성 및 실행
- **3-4주차**:
    - **2단계: Triplet 데이터셋 생성** 스크립트 작성
    - MuQ 모델 Triplet Loss 파인튜닝 코드 구현 및 학습 진행
- **5주차**:
    - 파인튜닝 모델 성능 평가 (정량적/정성적 평가)
    - FMA 데이터셋 전체에 대한 **최종 임베딩** 추출 및 FAISS 인덱스 구축
- **6-7주차**:
    - 백엔드 API 개발 (FastAPI): 사용자 인증, DB 스키마, 플레이리스트 CRUD
    - AI 서비스 연동 API 구현 및 프론트엔드 UI 개발 (React)
- **8주차**:
    - 전체 시스템 통합 및 버그 수정
    - 최종 보고서 및 발표 자료 작성

*상기 일정은 핵심 기능(플레이리스트 생성 및 공유) 기준이며, 소셜/게이미피케이션 기능은 추가 시간이 필요할 수 있습니다.*

---

## 8. 활용 방안 및 사업화 전략

- **개인 사용자**: 새로운 음악을 탐색하고 자신의 취향을 발견하며, 비슷한 취향의 사용자들과 소통하는 소셜 활동의 도구로 활용합니다.
- **작곡가/프로듀서**: 자신의 창작곡이나 데모곡을 시드(Seed)로 사용하여, 유사한 분위기의 레퍼런스를 찾거나 표절을 예방하기 위한 아이디어 발상 도구로 활용할 수 있습니다.
- **서비스 확장 및 사업화**:
    - **상용 서비스 즉시 적용**: 본 프로젝트의 AI 모델과 시스템은 FMA 데이터셋뿐만 아니라 **멜론, 스포티파이 등 상용 음원 DB에 즉시 적용 가능한 구조**입니다. 기업은 별도의 핵심 기술 개발 없이, 보유한 음원 데이터에 본 모델을 파인튜닝하여 고품질의 AI 추천 기능을 빠르게 도입할 수 있습니다.
    - **B2B API 제공**: 파인튜닝된 추천 모델을 다른 미디어 플랫폼이나 독립 개발자에게 API 형태로 제공하여 수익을 창출합니다.
    - **트렌드 분석 리포트 판매**: 축적된 사용자 데이터와 음악 분석 결과를 바탕으로, 음악 시장의 트렌드를 분석하는 리포트를 생성 및 판매하는 데이터 비즈니스로 확장할 수 있습니다.

---

## 9. 참고문헌 (References)

### 9.1. Core AI/ML Models & Libraries
- **MuQ & MuQ-MuLan**: Zhu, H., et al. (2025). MuQ: Self-Supervised Music Representation Learning with Mel Residual Vector Quantization. *arXiv preprint arXiv:2501.01108*.
- **Faiss**: Douze, M., et al. (2024). The Faiss library. *arXiv preprint arXiv:2401.08281*.
- **PyTorch**: Paszke, A., et al. (2019). PyTorch: An Imperative Style, High-Performance Deep Learning Library. *Advances in Neural Information Processing Systems*.

### 9.2. Key Methodologies
- **Music Information Retrieval (MIR)**:
    - Müller, M. (2015). *Fundamentals of Music Processing: Audio, Analysis, Algorithms, Applications*. Springer.
    - Casey, M., et al. (2008). Music Information Retrieval: Recent Developments and Applications. *IEEE Transactions on Audio, Speech, and Language Processing*.
- **Triplet Loss & Hard Negative Mining**:
    - Schroff, F., Kalenichenko, D., & Philbin, J. (2015). FaceNet: A Unified Embedding for Face Recognition and Clustering. *CVPR*.
    - Wu, C., et al. (2017). Sampling Matters in Deep Metric Learning. *ICCV*.

### 9.3. Evaluation & Visualization
- **t-SNE**: Maaten, L. van der, & Hinton, G. (2008). Visualizing Data using t-SNE. *Journal of Machine Learning Research*.
- **Silhouette Score**: Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*.

### 9.4. Features & Concepts
- **Recommender Systems**:
    - Ricci, F., Rokach, L., & Shapira, B. (2022). *Recommender Systems Handbook*. Springer.
    - Linden, G., Smith, B., & York, J. (2003). Amazon.com recommendations: Item-to-item collaborative filtering. *IEEE Internet Computing*.
- **Gamification**: Deterding, S., et al. (2011). From Game Design Elements to Gamefulness: Defining Gamification. *MindTrek'11*.

### 9.5. Datasets
- **FMA Dataset**: Defferrard, M., et al. (2016). FMA: A Dataset for Music Analysis. *ISMIR*.

### 9.6. Development Frameworks
- **FastAPI**: FastAPI, created by Sebastián Ramírez. https://fastapi.tiangolo.com/
- **React (Next.js)**: Next.js by Vercel. https://nextjs.org/
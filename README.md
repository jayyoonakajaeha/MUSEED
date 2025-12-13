# MUSEED: AI 플레이리스트 자동 생성 플랫폼 (AI Playlist Generator)

MUSEED는 사용자가 제공하는 '시드(Seed) 음악' 한 곡의 음악적, 감성적 특징을 AI가 심층 분석하여, 사용자의 숨겨진 취향까지 만족시키는 새로운 노래들로 구성된 맞춤형 플레이리스트를 자동으로 생성해주는 웹 플랫폼입니다.

MUSEED is a web platform that automatically generates personalized playlists by deeply analyzing the musical and emotional characteristics of a single 'Seed Music' provided by the user. It utilizes AI to discover songs that satisfy even the user's hidden tastes.

---

## 👤 제작자 (Creator)

- **이름 (Name)**: 윤재하 (Jaeha Yoon)
- **이메일 (Email)**: 613jay@sju.ac.kr
- **개발 (Role)**: 1인 단독 개발 (Single-handed Development)

---

## 📁 프로젝트 구조 (Project Structure)

- **`backend/`**: FastAPI 기반의 RESTful API 서버 코드 (FastAPI backend server code)
- **`frontend/`**: Next.js 기반의 웹 프론트엔드 코드 (Next.js frontend code)
- **`research/`**: AI 모델 학습, 평가 및 데이터 분석용 스크립트 (AI research, training, and evaluation scripts)
- **`models/`**: 학습된 모델 가중치 저장소 (Trained model weights)
- **`data/`**: 대용량 데이터셋 저장소 (Large datasets)

---

## ✨ 주요 기능 (Key Features)

- **AI 기반 플레이리스트 자동 생성 (AI Playlist Generation)**: 파인튜닝된 MuQ 오디오 인코더를 활용하여 시드 음악의 미묘한 특징까지 이해하고 유사한 곡들을 찾아냅니다. (Uses a fine-tuned MuQ audio encoder to analyze seed music and find similar tracks.)
- **스마트 오디오 플레이어 (Smart Audio Player)**: 앨범 아트, 진행 바, 대기열(Queue) 기능을 갖춘 반응형 플레이어로 끊김 없는 음악 감상이 가능합니다. (Responsive player with album art, progress bar, and queue for seamless listening.)
- **사용자 인증 및 프로필 (User Auth & Profile)**: 안전한 회원가입/로그인, 프로필 관리, 팔로우/팔로잉, 활동 피드(Feed) 기능을 제공합니다. (Secure signup/login, profile management, follow system, and activity feed.)
- **플레이리스트 관리 (Playlist Management)**: 생성, 수정(드래그 앤 드롭 순서 변경), 삭제, 공개/비공개 설정, 좋아요 기능을 지원합니다. (Create, edit, reorder, delete, and like playlists.)
- **소셜 기능 (Social Features)**: 다른 사용자의 플레이리스트를 탐색하고, 좋아요를 누르고, 활동을 피드에서 확인할 수 있습니다. (Explore and like other users' playlists.)
- **모바일 최적화 (Mobile Optimization)**: 모든 기능이 모바일 환경에서도 완벽하게 동작하도록 반응형으로 설계되었습니다. (Fully responsive design for mobile devices.)

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion
- **Backend**: FastAPI, Python, SQLAlchemy, Pydantic
- **Database**: PostgreSQL
- **Async Queue**: Redis, Celery (for Background AI Tasks)
- **AI / ML**: PyTorch, MuQ (Music Quantization), Faiss (Vector Search)
- **Infra**: Docker, Docker Compose, Cloudflare Tunnel

---



---



## 🚀 시작하기 (Getting Started)

로컬 컴퓨터에서 프로젝트를 설정하고 실행하기 위한 안내입니다. 교수님 및 평가자를 위한 **[소스코드 제출용 실행 가이드]**입니다.

### 1. 사전 준비 및 폴더 구조 (Prerequisites & Directory Structure)

이 프로젝트는 **MUSEED**(본 프로젝트)와 **MuQ**(외부 라이브러리)가 **형제 폴더(Sibling Directory)** 로 위치해야 실행됩니다.

1.  **작업 폴더 생성:**
    ```bash
    mkdir MusicAI_Workspace
    cd MusicAI_Workspace
    ```

2.  **Github 저장소 클론 (Clone Repositories):**
    ```bash
    # 1. MUSEED (본 프로젝트)
    git clone https://github.com/jayyoonakajaeha/MUSEED.git

    # 2. MuQ (필수 외부 라이브러리)
    git clone https://github.com/tencent-ailab/MuQ.git

    # 3. FMA (데이터셋 스크립트 참조용)
    git clone https://github.com/mdeff/fma.git
    ```

### 2. 데이터셋 구축 가이드 (Data Construction)
이 프로젝트의 핵심인 `data/` 및 `models/` 폴더를 처음부터 구축(Reproduce)하는 방법입니다.

#### 1단계: FMA 데이터셋 준비 (FMA Dataset Preparation)
FMA 메타데이터와 오디오 파일은 `MUSEED` 폴더 밖 형제 디렉토리(`../../fma`)에 위치해야 합니다.
```bash
# 1. FMA 데이터 폴더 생성 (이미 git clone fma를 했다면 폴더가 있을 수 있음)
# MUSICAI_Workspace/fma/data 위치에 데이터를 다운로드합니다.
mkdir -p MusicAI_Workspace/fma/data
cd MusicAI_Workspace/fma/data

# 2. 메타데이터 다운로드 및 압축 해제
curl -O https://os.unil.cloud.switch.ch/fma/fma_metadata.zip
unzip fma_metadata.zip
# 결과: fma/data/fma_metadata 폴더 생성

# 3. 원본 오디오 다운로드 (fma_full 사용 시 800GB 주의)
# curl -O https://os.unil.cloud.switch.ch/fma/fma_full.zip
# unzip fma_full.zip
```

#### 2단계: 메타데이터 생성 (Metadata Generation)
다음 스크립트를 순서대로 실행하여 `.jsonl` 메타데이터 파일을 생성합니다.
```bash
cd MUSEED/research

# 1. Jamendo 데이터셋 다운로드
# (음원 파일은 Sibling 폴더인 '../../jamendo_formatted'에 저장됨)
python prepare_jamendo_dataset.py --output_dir ../../jamendo_formatted --limit 200

# 2. FMA 데이터셋 전처리
# (FMA 메타데이터가 '../../fma/data/fma_metadata'에 있어야 함)
python preprocess_fma_genres.py 

# 3. 데이터셋 분할 (Train/Test Split)
# (결과물은 내부 'data/' 폴더에 저장됨)
python split_dataset.py
```
**결과물:** `../data/` (즉, `MUSEED/data`) 폴더에 `train_metadata.jsonl` 등이 생성됩니다.

#### 3단계: 임베딩 추출 (Embedding Extraction)
오디오 파일에서 MuQ 임베딩을 추출합니다. (시간이 오래 걸립니다 - GPU 권장)
```bash
# 통합 임베딩 추출 실행
python extract_embeddings_mean_pooling.py \
  --input_path ../data/train_metadata.jsonl \
  --output_dir ../data/embeddings_contrastive_v2_mean
```
**결과물:** `../data/embeddings_contrastive_v2_mean/` 폴더에 `.npy` 파일들이 생성됩니다.

#### 4단계: FAISS 인덱스 빌드 (Build Search Index)
생성된 임베딩을 검색 가능한 인덱스 파일로 변환합니다.
```bash
python build_faiss_index.py
```
**결과물:** `../models/faiss_index.bin` 파일이 생성됩니다.

**최종 폴더 구조 확인:**
```
MusicAI_Workspace/
├── MUSEED/            # 본 프로젝트
├── MuQ/               # 외부 라이브러리
├── data/              # 메타데이터 및 임베딩 (train_metadata.jsonl 등)
├── jamendo_formatted/ # Jamendo 음원 파일
└── fma/               # FMA 음원 파일
```

---

### 3. 백엔드 설정 및 실행 (Backend)

1.  **디렉토리 이동:**
    ```bash
    cd MUSEED/backend
    ```

2.  **가상환경 생성 및 의존성 설치:**
    ```bash
    conda create --name museed_backend python=3.10 -y
    conda activate museed_backend
    pip install -r requirements.txt
    ```

3.  **데이터베이스 설정 (Database Setup):**
    *   PostgreSQL이 설치되어 있어야 합니다.
    *   `psql` 또는 pgAdmin을 사용하여 DB를 생성합니다:
    ```sql
    CREATE DATABASE museed_db;
    GRANT ALL PRIVILEGES ON DATABASE museed_db TO postgres;
    -- (비밀번호: 'your_password'로 가정, .env 파일에서 수정 가능)
    ```
    *   `backend/.env` 파일을 생성하고 아래 내용을 추가하세요:
    ```bash
    DATABASE_URL="postgresql://postgres:your_password@localhost:5432/museed_db"
    ```

4.  **실행 (Run Server):**
    ```bash
    # MuQ 경로 자동 인식 포함된 스크립트 실행
    ./run_backend.sh
    ```
    *   서버 주소: `http://localhost:8000`

---

### 4. AI 워커 실행 (AI Worker)

AI 플레이리스트 생성 기능을 사용하려면 워커를 별도 터미널에서 실행해야 합니다.

1.  **새 터미널 열기** 후 `backend` 폴더로 이동.
2.  **실행:**
    ```bash
    conda activate museed_backend
    ./run_worker.sh
    ```
    *   "Loading resources..." 메시지와 함께 MuQ 모델이 로드되면 준비 완료입니다.

---

### 5. 프론트엔드 설정 및 실행 (Frontend)

1.  **디렉토리 이동:**
    ```bash
    cd ../frontend
    ```

2.  **의존성 설치 및 실행:**
    ```bash
    pnpm install
    pnpm dev
    ```
    *   웹사이트 접속: `http://localhost:3000` (또는 3001)

---

## 🔬 연구 및 모델 개발 (Research & Model Config)
*   **`evaluate_model.py`**: KNN 정확도, Linear Probe F1-Score, Silhouette Score 등 정량적 지표를 측정하고 t-SNE 시각화 결과를 생성합니다.

### 3. 외부 접속 설정 (External Access)
 
 안정적인 외부 접속을 위해 **Cloudflare Tunnel** 사용을 권장합니다. (Cloudflare Tunnel is recommended for stable external access.)
 
 1.  **Cloudflare Tunnel 설치 (Install cloudflared):**
     *   [공식 문서](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)를 일거 설치합니다.
 
 2.  **터널 실행 (Run Tunnel):**
     *   **개인 도메인이 없는 경우 (Free Random URL):**
         ```bash
         cloudflared tunnel --url http://localhost:3000
         ```
     *   **고정 도메인이 있는 경우 (Custom Domain):** `cloudflared.yml` 설정 후:
         ```bash
         cloudflared tunnel --config cloudflared.yml run
         ```
 
 ---
 
## 🐳 Docker로 서비스 재현하기 (How to Reproduce with Docker)

이 가이드는 빈 서버 환경에서 MUSEED 서비스를 처음부터 구축하고 실행하는 모든 과정을 상세히 설명합니다.

### 1. 사전 요구사항 (Prerequisites)
이 프로젝트를 실행하기 위해 필요한 데이터와 도구입니다.
*   **하드웨어**: NVIDIA GPU (VRAM 8GB+ 권장), 2TB 이상의 저장 공간.
*   **소프트웨어**: 
    *   [Docker & Docker Desktop](https://www.docker.com/products/docker-desktop/)
    *   [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (Linux 필수)

### 2. 디렉토리 구조 및 준비 (Directory Structure)
다음과 같이 `workspace` 폴더 아래에 프로젝트와 데이터가 배치되어야 합니다.
```plaintext
workspace/
├── MUSEED/                  # 이 저장소 (Main Project)
├── MuQ/                     # AI 모델 라이브러리 (Sibling Repository)
├── fma_full/                # FMA 데이터셋 (106,574 트랙, 882GB)
│   ├── 000/
│   ├── 001/
│   └── ...
└── jamendo/                 # Jamendo 데이터셋 (MTG-Jamendo)
    ├── audio/
    └── ...
```

### 3. 단계별 설치 (Step-by-Step Installation)

**Step 1: 저장소 클론 (Clone Repositories)**
두 개의 저장소(`MUSEED`, `MuQ`)를 동일한 상위 폴더 내에 내려받습니다.
```bash
mkdir workspace && cd workspace
git clone https://github.com/jayyoonakajaeha/MUSEED.git
git clone <MuQ-Repo-URL> MuQ  # MuQ 라이브러리 접근 권한 필요
```

**Step 2: MuQ 라이브러리 준비**
Docker 빌드 시 외부 파일 접근 제한을 해결하기 위해, 로컬의 MuQ 코드를 프로젝트 내부로 복사합니다.
```bash
cd MUSEED
chmod +x prepare_docker_build.sh
./prepare_docker_build.sh
```

**Step 3: 환경 변수 설정 (.env)**
`MUSEED/` 디렉토리 안에 `.env` 파일을 생성하고, **실제 데이터 경로**를 입력해 주세요.
```bash
# .env 파일 생성 및 편집
nano .env
```
```env
# --- 필수 설정 ---
# 2번 항목에서 준비한 데이터 폴더의 절대 경로를 입력하세요.
FMA_DATA_PATH=/home/username/workspace/fma_full
JAMENDO_DATA_PATH=/home/username/workspace/jamendo

# 데이터베이스 비밀번호 (변경 가능)
POSTGRES_PASSWORD=secure_password
```

**Step 4: 서비스 실행 (Run)**
MUSEED는 커스텀 MuQ 라이브러리를 사용하므로, Docker Hub에서 이미지를 받아오는(`docker pull`) 방식 대신 **로컬 빌드(`--build`)** 방식을 사용합니다.
```bash
docker-compose up -d --build
```
이 명령어는 로컬 코드를 기반으로 Docker 이미지를 생성하고 컨테이너를 실행합니다.
*   **초기 구동 확인**: `docker-compose logs -f backend` 명령어로 서버가 시작될 때까지(약 1~2분) 기다립니다.
*   **접속 주소**: [http://localhost:3000](http://localhost:3000)

### 4. 문제 해결 (Troubleshooting)
*   **"MuQ module not found" 에러**: `Step 2`의 `./prepare_docker_build.sh`를 실행했는지 확인하세요.
*   **"CUDA error" 또는 GPU 미인식**: 호스트 머신에 `nvidia-driver`와 `nvidia-container-toolkit`이 설치되었는지 확인하고, `docker-compose exec backend nvidia-smi`를 입력하여 GPU가 보이는지 체크하세요.
*   **멈춤 현상**: `docker-compose.yml` 파일에서 워커 설정이 `pool=solo`로 되어 있는지 확인하세요. (기본값 설정됨)
 
 ---
 
 ## 🔑 환경 변수 보안 (Environment Variables)
 
 보안을 위해 모든 민감한 정보는 `.env` 파일로 관리하며, GitHub에는 업로드되지 않습니다.
 
 1. **Backend (`backend/.env`):**
    ```env
    DATABASE_URL="postgresql://..."
    JAMENDO_CLIENT_ID="your_client_id_here"  # research 스크립트에서 사용
    ```
 
 > **Note:** `research/` 폴더의 스크립트들은 자동으로 `backend/.env` 파일을 참조하도록 설정되어 있습니다.


---

## 🔬 연구 및 모델 개발 (Research & Model Development)

MUSEED의 핵심 AI 엔진 개발 및 실험 코드는 `research/` 디렉토리에 있습니다.

### 1. 모델 학습 (Model Training)
*   **`train_contrastive.py`**: SimCLR 기반의 대조 학습(Contrastive Learning)을 수행합니다.
*   **`train_triplet_loss.py`**: Hard Negative Mining을 포함한 Triplet Loss 학습을 수행합니다.

### 2. 모델 평가 (Model Evaluation)
*   **`evaluate_model.py`**: KNN 정확도, Linear Probe F1-Score, Silhouette Score 등 정량적 지표를 측정하고 t-SNE 시각화 결과를 생성합니다.

---

&copy; 2025 MUSEED. All rights reserved. Created by Jaeha Yoon.

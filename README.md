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
- **Infra**: Docker, Docker Compose, ngrok (Tunneling)

---

## 🔬 연구 및 모델 개발 (Research & Model Development)

MUSEED의 핵심 AI 엔진을 개발하기 위한 연구 코드는 `research/` 디렉토리에 정리되어 있습니다. 재현 가능한(Reproducible) 파이프라인을 위해 다음 4단계의 핵심 스크립트가 제공됩니다.

### 1. 데이터 준비 (Data Preparation)
*   **`prepare_jamendo_dataset.py`**: Jamendo 데이터셋의 다운로드부터 메타데이터 생성, 장르 매핑까지 한 번에 수행합니다.
*   **`split_dataset.py`**: 다축 분석 결과를 바탕으로 데이터셋을 훈련/테스트 셋으로 층화 추출(Stratified Split)합니다.

### 2. 임베딩 추출 (Embedding Extraction)
*   **`extract_embeddings.py`**: 통합 임베딩 추출 스크립트입니다.
    *   **주요 기능:** Sliding Window (10초, Overlap 없음), 배치 처리(Batch Processing), 다양한 모델(MuQ, MuLan) 지원.
    *   **사용법:** `python extract_embeddings.py --model_path <ckpt> --input_path <jsonl> ...`

### 3. 모델 학습 (Model Training)
*   **`train_contrastive.py`**: SimCLR 기반의 대조 학습(Contrastive Learning)을 수행합니다.
*   **`train_triplet_loss.py`**: Hard Negative Mining을 포함한 Triplet Loss 학습을 수행합니다.

### Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- NVIDIA Container Toolkit (for GPU support)
- FMA Dataset & Jamendo Dataset (Raw Audio)

### 1. Prepare Environment
Create a `.env` file in `backend/` consistent with `.env.example`.
Ensure your data paths are set.

### 2. Prepare Local Library
We vendor the `MuQ` library to handle Docker context limits. Run:
```bash
./prepare_docker_build.sh
```

### 3. Build and Run
```bash
# Set paths to your local 2TB Storage
export FMA_DATA_PATH="/path/to/fma"
export JAMENDO_DATA_PATH="/path/to/jamendo"

docker-compose up --build -d
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/docs`
- Celery Worker: Running in background

### 4. GPU Verification
Check if the backend container sees the GPU:
```bash
docker-compose exec backend nvidia-smi
```

---

## 서비스 소개 (Introduction)
*   **`evaluate_model.py`**: KNN 정확도, Linear Probe F1-Score, Silhouette Score 등 정량적 지표를 측정하고 t-SNE 시각화 결과를 생성합니다.

---

## 🚀 시작하기 (Getting Started)

로컬 컴퓨터에서 프로젝트를 설정하고 실행하기 위한 안내입니다.

### 사전 준비물 (Prerequisites)

- [Node.js](https://nodejs.org/) (v18+)
- [pnpm](https://pnpm.io/installation)
- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Miniconda or Anaconda)
- [PostgreSQL](https://www.postgresql.org/download/)
- **MuQ Library**: 상위 폴더에 `MuQ` 저장소를 Clone 해야 합니다. (Required as sibling directory `../MuQ`)

### 1. 백엔드 설정 (Backend Setup)

1.  **백엔드 디렉토리로 이동합니다 (Navigate to backend directory):**
    ```bash
    cd MUSEED/backend
    ```

2.  **Conda 가상환경을 생성하고 활성화합니다 (Create and activate Conda environment):**
    ```bash
    conda create --name museed_backend python=3.10 -y
    conda activate museed_backend
    ```

3.  **Python 의존성을 설치합니다 (Install dependencies):**
    ```bash
    pip install -r requirements.txt
    ```

4.  **PostgreSQL을 설정합니다 (Setup PostgreSQL):**
    - PostgreSQL 서버가 실행 중인지 확인합니다. (Ensure PostgreSQL server is running.)
    - `psql`에 접속하여 프로젝트 전용 데이터베이스와 사용자를 생성합니다. (Create database and user.)
      ```sql
      -- 'museed_db' 데이터베이스 생성
      CREATE DATABASE museed_db;
      
      -- 'postgres' 사용자에게 'museed_db'에 대한 모든 권한 부여
      GRANT ALL PRIVILEGES ON DATABASE museed_db TO postgres;
      
      -- 'postgres' 사용자의 비밀번호 설정 (아직 설정하지 않은 경우)
      \password postgres 
      ```

5.  **환경 변수 파일을 생성합니다 (Create .env file):**
    - `backend` 디렉토리 안에 `.env` 파일을 생성합니다.
    - 아래 내용을 파일에 추가합니다. (Add the following content.)
      ```
      DATABASE_URL="postgresql://postgres:your_password@localhost:5432/museed_db"
      ```
    - `your_password` 부분을 실제 설정한 비밀번호로 교체합니다.

6.  **백엔드 서버를 실행합니다 (Run backend server):**
    ```bash
    ./run_backend.sh
    # or
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### 2. 프론트엔드 설정 (Frontend Setup)

1.  **프론트엔드 디렉토리로 이동합니다 (Navigate to frontend directory):**
    ```bash
    cd MUSEED/frontend
    ```

2.  **Node.js 의존성을 설치합니다 (Install dependencies):**
    ```bash
    pnpm install
    ```

3.  **운영 모드로 빌드 및 실행합니다 (Build and run):**
    ```bash
    pnpm run build
    pnpm start
    ```
    프론트엔드 서버가 `http://localhost:3000`에서 실행됩니다.

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
&copy; 2025 MUSEED. All rights reserved. Created by Jaeha Yoon.

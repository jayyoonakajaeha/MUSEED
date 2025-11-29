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
- **AI / ML**: PyTorch, MuQ (Music Quantization), Faiss (Vector Search)
- **Infra**: ngrok (Tunneling), PM2 (Process Management)

---

## 🚀 시작하기 (Getting Started)

로컬 컴퓨터에서 프로젝트를 설정하고 실행하기 위한 안내입니다.

### 사전 준비물 (Prerequisites)

- [Node.js](https://nodejs.org/) (v18+)
- [pnpm](https://pnpm.io/installation)
- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Miniconda or Anaconda)
- [PostgreSQL](https://www.postgresql.org/download/)

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

학교 네트워크나 공유기 포트 포워딩이 어려운 환경에서도 `ngrok`을 사용하여 외부에서 접속할 수 있습니다.

1.  **ngrok 실행 (Run ngrok):**
    ```bash
    ngrok http 3000
    ```
2.  생성된 `https://xxxx.ngrok-free.app` 주소로 접속하면 모바일 등 외부 기기에서도 모든 기능을 사용할 수 있습니다. (Access the generated URL.)

---
&copy; 2025 MUSEED. All rights reserved. Created by Jaeha Yoon.

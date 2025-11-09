# MUSEED: AI 플레이리스트 자동 생성 플랫폼

MUSEED는 사용자가 제공하는 '시드(Seed) 음악' 한 곡의 음악적, 감성적 특징을 AI가 심층 분석하여, 사용자의 숨겨진 취향까지 만족시키는 새로운 노래들로 구성된 맞춤형 플레이리스트를 자동으로 생성해주는 웹 플랫폼입니다.

## ✨ 주요 기능

- **AI 기반 플레이리스트 자동 생성**: 파인튜닝된 MuQ 오디오 인코더를 활용하여 시드 음악의 미묘한 특징까지 이해하고 유사한 곡들을 찾아냅니다.
- **사용자 인증**: 안전한 회원가입 및 로그인 기능을 제공합니다.
- **모던 프론트엔드**: Next.js와 shadcn/ui로 구축되어 반응형의 미려한 사용자 경험을 제공합니다.
- **확장 가능한 백엔드**: FastAPI와 PostgreSQL을 기반으로 설계되어 향후 기능 확장에 용이합니다.

## 🛠️ 기술 스택

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python, SQLAlchemy
- **Database**: PostgreSQL
- **AI / ML**: PyTorch, MuQ, Faiss

## 🚀 시작하기

로컬 컴퓨터에서 프로젝트를 설정하고 실행하기 위한 안내입니다.

### 사전 준비물

- [Node.js](https://nodejs.org/) (v18 이상)
- [pnpm](https://pnpm.io/installation)
- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Miniconda 또는 Anaconda)
- [PostgreSQL](https://www.postgresql.org/download/)

### 1. 백엔드 설정

1.  **백엔드 디렉토리로 이동합니다:**
    ```bash
    cd MUSEED/backend
    ```

2.  **Conda 가상환경을 생성하고 활성화합니다:**
    ```bash
    conda create --name museed_backend python=3.10 -y
    conda activate museed_backend
    ```

3.  **Python 의존성을 설치합니다:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **PostgreSQL을 설정합니다:**
    - PostgreSQL 서버가 실행 중인지 확인합니다.
    - `psql`에 접속하여 프로젝트 전용 데이터베이스와 사용자를 생성합니다.
      ```sql
      -- 'museed_db' 데이터베이스 생성
      CREATE DATABASE museed_db;
      
      -- 'postgres' 사용자에게 'museed_db'에 대한 모든 권한 부여
      GRANT ALL PRIVILEGES ON DATABASE museed_db TO postgres;
      
      -- 'postgres' 사용자의 비밀번호 설정 (아직 설정하지 않은 경우)
      \password postgres 
      ```

5.  **환경 변수 파일을 생성합니다:**
    - `backend` 디렉토리 안에 `.env` 파일을 생성합니다.
    - 아래 내용을 파일에 추가합니다. 이 파일은 Git에 의해 무시됩니다.
      ```
      DATABASE_URL="postgresql://postgres:your_password@localhost:5432/museed_db"
      ```
    - `your_password` 부분을 실제 설정한 비밀번호로 교체합니다.

6.  **백엔드 서버를 실행합니다:**
    ```bash
    uvicorn app.main:app --reload
    ```
    백엔드 서버가 `http://localhost:8000`에서 실행됩니다.

### 2. 프론트엔드 설정

1.  **프론트엔드 디렉토리로 이동합니다:**
    ```bash
    cd MUSEED/frontend
    ```

2.  **Node.js 의존성을 설치합니다:**
    ```bash
    pnpm install
    ```

3.  **프론트엔드 개발 서버를 실행합니다:**
    ```bash
    pnpm dev
    ```
    프론트엔드 서버가 `http://localhost:3000`에서 실행됩니다.

---

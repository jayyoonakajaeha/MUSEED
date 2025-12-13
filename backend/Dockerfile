FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치
# libsndfile1: soundfile/librosa용
# ffmpeg: 오디오 처리용
# git: 일부 pip 설치용
# procps: ps 명령어용 (선택적 디버깅)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# MuQ 로컬 패키지 설치 (Vendored)
COPY muq_pkg muq_pkg
RUN pip install --no-cache-dir -e muq_pkg

# 애플리케이션 코드 복사
COPY . .

# 환경변수 파일 플레이스홀더 복사 (Compose가 볼륨으로 덮어씀)
COPY .env .env

# 스크립트 실행 권한 부여
RUN chmod +x run_backend.sh

# 포트 노출 (FastAPI)
EXPOSE 8000

# 기본 명령어 (워커용은 Compose에서 재정의됨)
CMD ["./run_backend.sh"]

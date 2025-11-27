#!/bin/bash

# MuQ 가상환경 활성화
conda activate museed_be
service postgresql start

# uvicorn 서버 실행 (모듈 경로 문제 해결)
# 현재 디렉토리가 backend일 때 app 패키지를 인식하도록 실행
echo "Starting MUSEED Backend Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

#!/usr/bin/env bash
# 개발 서버 실행 스크립트
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip
  ./.venv/bin/pip install -r requirements.txt
fi

./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

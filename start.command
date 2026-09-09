#!/bin/bash
# ============================================================
#  macOS / Linux 더블클릭 실행기 (Finder에서 더블클릭 가능)
#  최초 1회 실행 권한 부여:  chmod +x start.command
# ============================================================
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "[최초 설치] 가상환경 생성 + 의존성 설치..."
  python3 -m venv .venv
  ./.venv/bin/python -m pip install --upgrade pip
  ./.venv/bin/pip install -r requirements.txt
fi

./.venv/bin/python run.py --port 8000

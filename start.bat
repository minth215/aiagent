@echo off
REM ============================================================
REM  프로그램 목록/업무흐름도 관리 - Windows 실행기
REM  (보통은 바탕화면 아이콘으로 실행됩니다. 직접 더블클릭도 가능)
REM ============================================================
cd /d "%~dp0"

REM 최초 1회: 가상환경 자동 생성 + 의존성 설치
if not exist ".venv\Scripts\python.exe" (
  echo [최초 설치] 가상환경을 만들고 의존성을 설치합니다...
  python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip
  if exist "wheels\" (
    REM 폐쇄망: 미리 반입한 wheels 폴더에서 오프라인 설치
    .venv\Scripts\pip install --no-index --find-links=wheels -r requirements.txt
  ) else (
    .venv\Scripts\pip install -r requirements.txt
  )
)

REM 서버 실행 (run.py가 브라우저를 자동으로 엽니다. 이미 떠 있으면 브라우저만 엽니다)
.venv\Scripts\python run.py --port 8000

REM 오류 확인용 (창을 직접 띄워 실행했을 때만 의미 있음)
if errorlevel 1 pause

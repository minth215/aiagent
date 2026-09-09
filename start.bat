@echo off
REM ============================================================
REM  프로그램 목록/업무흐름도 관리 - Windows 더블클릭 실행기
REM  이 파일을 더블클릭하면 서버가 뜨고 브라우저가 자동으로 열립니다.
REM  (터미널에 python 명령을 직접 칠 필요가 없습니다)
REM ============================================================
cd /d "%~dp0"

REM 최초 1회: 가상환경 자동 생성 + 의존성 설치 (인터넷 필요)
if not exist ".venv\Scripts\python.exe" (
  echo [최초 설치] 가상환경을 만들고 의존성을 설치합니다...
  python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip
  .venv\Scripts\pip install -r requirements.txt
)

REM 서버 실행 (run.py가 브라우저를 자동으로 엽니다). 포트는 필요시 바꾸세요.
.venv\Scripts\python run.py --port 8000

pause

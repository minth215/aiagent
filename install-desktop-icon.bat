@echo off
REM ============================================================
REM  최초 1회만 실행: 바탕화면에 실행 아이콘을 만들어 줍니다.
REM  이후로는 바탕화면 아이콘만 더블클릭하면 (CMD 창 없이) 웹앱이 뜹니다.
REM ============================================================
setlocal
cd /d "%~dp0"

echo.
echo === 1/2. 최초 설치 (가상환경 + 의존성) ===
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 (
    echo [오류] Python 이 설치되어 있지 않거나 PATH 에 없습니다.
    echo        python.org 에서 설치 후 다시 실행하세요.
    pause & exit /b 1
  )
  .venv\Scripts\python -m pip install --upgrade pip
  if exist "wheels\" (
    .venv\Scripts\pip install --no-index --find-links=wheels -r requirements.txt
  ) else (
    .venv\Scripts\pip install -r requirements.txt
  )
) else (
  echo   이미 설치됨 - 건너뜀
)

echo.
echo === 2/2. 바탕화면 아이콘 생성 ===
set "TARGET=%~dp0start-hidden.vbs"
set "WORKDIR=%~dp0"
set "ICON=%~dp0app\static\app.ico"
set "LNKNAME=프로그램목록관리"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\%LNKNAME%.lnk');" ^
  "$lnk.TargetPath = 'wscript.exe';" ^
  "$lnk.Arguments = '\"%TARGET%\"';" ^
  "$lnk.WorkingDirectory = '%WORKDIR%';" ^
  "if (Test-Path '%ICON%') { $lnk.IconLocation = '%ICON%' } else { $lnk.IconLocation = 'shell32.dll,14' };" ^
  "$lnk.Description = '프로그램 목록/업무흐름도 관리';" ^
  "$lnk.Save()"

if errorlevel 1 (
  echo [오류] 아이콘 생성 실패.
) else (
  echo   바탕화면에 '%LNKNAME%' 아이콘을 만들었습니다.
  echo   이제 그 아이콘을 더블클릭하면 웹앱이 뜹니다.
)
echo.
pause
endlocal

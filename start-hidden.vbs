' ============================================================
'  콘솔 창 없이 조용히 실행하는 Windows 런처.
'  - 이 파일을 더블클릭하면 검은 창 없이 백그라운드로 서버가 뜹니다.
'  - "항상 켜두기"(시작프로그램 등록)에 이 파일을 쓰면 깔끔합니다.
'  - 종료하려면 작업 관리자에서 python 프로세스를 끝내면 됩니다.
' ============================================================
Set sh = CreateObject("WScript.Shell")
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
sh.CurrentDirectory = scriptDir
' 0 = 창 숨김, False = 종료를 기다리지 않음
sh.Run "cmd /c """"" & scriptDir & "start.bat""""", 0, False

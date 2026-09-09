' ============================================================
'  콘솔(CMD) 창 없이 조용히 실행하는 Windows 런처.
'  바탕화면 아이콘이 이 파일을 가리키게 하면, 더블클릭 시
'  검은 창 없이 웹앱이 뜨고 브라우저가 열립니다.
'  (install-desktop-icon.bat 이 이 파일로 아이콘을 만들어 줍니다)
' ============================================================
Set sh = CreateObject("WScript.Shell")
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
sh.CurrentDirectory = scriptDir
' 0 = 창 숨김, False = 종료를 기다리지 않음
sh.Run "cmd /c """ & scriptDir & "start.bat""", 0, False

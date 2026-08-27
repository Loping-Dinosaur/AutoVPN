Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
pythonw = scriptDir & "\.venv\Scripts\pythonw.exe"
mainScript = scriptDir & "\vpn_auto.py"

WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & pythonw & """ """ & mainScript & """", 0, False

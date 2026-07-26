' Portable silent launcher — uses the folder where this .vbs lives
Option Explicit

Dim fso, shell, scriptDir, cmd, rc
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = scriptDir

' Prefer "py -3w" (windowless), then pythonw on PATH
If HasCommand("py") Then
  cmd = "py -3w """ & scriptDir & "\desktop_app.py"""
ElseIf HasCommand("pythonw") Then
  cmd = "pythonw """ & scriptDir & "\desktop_app.py"""
ElseIf HasCommand("python") Then
  cmd = "python """ & scriptDir & "\desktop_app.py"""
Else
  MsgBox "Python not found." & vbCrLf & vbCrLf & _
         "Install Python 3 and ensure py/python is on PATH." & vbCrLf & _
         "Then run: pip install -r requirements.txt", _
         vbCritical, "UPS Monitor"
  WScript.Quit 1
End If

' 0 = hidden window, False = do not wait
shell.Run cmd, 0, False
WScript.Quit 0

Function HasCommand(name)
  On Error Resume Next
  Dim r
  r = shell.Run("cmd /c where " & name & " >nul 2>&1", 0, True)
  HasCommand = (r = 0)
  On Error GoTo 0
End Function

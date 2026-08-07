' ============================================================
'  ULTIMA FC 27 - Launcher Oculto del Servidor
'  Este VBScript inicia el servidor de forma completamente
'  invisible (sin ventana de consola ni flash).
'  Diseñado para ejecutarse al arranque de Windows o bajo demanda.
' ============================================================

Dim objShell, fso, scriptDir, parentDir, psScript

Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
parentDir = fso.GetParentFolderName(scriptDir)

objShell.CurrentDirectory = scriptDir

' Ruta al script PowerShell de resiliencia
psScript = scriptDir & "\start_server_hidden.ps1"

If fso.FileExists(psScript) Then
    objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & psScript & """", 0, False
End If

Set objShell = Nothing
Set fso = Nothing

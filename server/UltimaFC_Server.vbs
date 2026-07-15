' ============================================================
'  ULTIMA FC - Launcher Oculto del Servidor
'  Este VBScript inicia el servidor de forma completamente
'  invisible (sin ventana de consola ni flash).
'  Diseñado para ejecutarse al arranque de Windows.
' ============================================================

Dim objShell, scriptDir, psScript

Set objShell = CreateObject("WScript.Shell")

' Obtener la ruta del directorio donde está este VBS
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Ruta al script PowerShell de resiliencia
psScript = scriptDir & "\start_server_hidden.ps1"

' Ejecutar PowerShell oculto (-WindowStyle Hidden) con bypass de política
' El "0" al final de Run() = ventana oculta, False = no esperar a que termine
objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & psScript & """", 0, False

Set objShell = Nothing

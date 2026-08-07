' ============================================================
'  ULTIMA FC 27 - Launcher Oculto del Servidor Central
'  Ejecuta el servidor en 2do plano sin ventana de consola.
' ============================================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' Si existe el script VBS del servidor en /server, ejecutarlo directamente
serverVbs = scriptDir & "\server\UltimaFC_Server.vbs"
batFile = scriptDir & "\iniciar_servidor.bat"

If fso.FileExists(serverVbs) Then
    WshShell.Run "wscript.exe """ & serverVbs & """", 0, False
ElseIf fso.FileExists(batFile) Then
    WshShell.Run "cmd /c """ & batFile & """", 0, False
End If

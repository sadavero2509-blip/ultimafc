@echo off
cd /d "%~dp0"

:: Cerrar procesos anteriores para asegurar un inicio limpio
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ssh.exe >nul 2>&1

:: 1. Iniciar servidor python
start /b .venv\Scripts\python.exe server\app.py > server.log 2>&1

:: Esperar a que levante
timeout /t 2 >nul

:: 2. Iniciar tunel SSH en segundo plano con bypass de llaves
set SSH_KEY_OPT=
if exist "%USERPROFILE%\FutbolGame" (
    set SSH_KEY_OPT=-i "%USERPROFILE%\FutbolGame"
)

start /b ssh %SSH_KEY_OPT% -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -R neofutbol-sadav:80:127.0.0.1:25565 serveo.net > tunnel.log 2>&1

:: Esperar 1 segundo
timeout /t 1 >nul

:: 3. Ejecutar auto-configurador para enlazar la URL al cliente
.venv\Scripts\python.exe scratch\update_tunnel_url.py

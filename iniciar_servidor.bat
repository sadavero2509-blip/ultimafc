@echo off
cd /d "%~dp0"

:: Cerrar procesos anteriores para asegurar un inicio limpio
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ssh.exe >nul 2>&1

:: 1. Iniciar servidor python
start /b .venv\Scripts\python.exe server\app.py > server.log 2>&1

:: Esperar a que levante usando ping (no interactivo y compatible)
ping 127.0.0.1 -n 3 >nul

:: 2. Configuracion de clave SSH
set SSH_KEY_OPT=
if exist "%USERPROFILE%\FutbolGame" (
    set SSH_KEY_OPT=-i "%USERPROFILE%\FutbolGame"
)

:: ============================================================
:: LOOP DE RESILIENCIA - Reinicia el tunel si se cae
:: ============================================================
:tunnel_loop

:: Verificar que el servidor python siga vivo, si no, reiniciarlo
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if errorlevel 1 (
    echo [%date% %time%] Servidor Python caido. Reiniciando... >> server_data\server_log.txt
    start /b .venv\Scripts\python.exe server\app.py > server.log 2>&1
    ping 127.0.0.1 -n 3 >nul
)

:: Iniciar tunel SSH
echo [%date% %time%] Iniciando tunel SSH... >> server_data\server_log.txt
start /b ssh %SSH_KEY_OPT% -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -R neofutbol-sadav:80:127.0.0.1:25565 serveo.net > tunnel.log 2>&1

:: Esperar a que el tunel se establezca
ping 127.0.0.1 -n 7 >nul

:: 3. Ejecutar auto-configurador para enlazar la URL al cliente
.venv\Scripts\python.exe scratch\update_tunnel_url.py
echo [%date% %time%] URL actualizada. >> server_data\server_log.txt

:: Esperar a que el tunel SSH termine (si se cae, el loop lo reinicia)
:wait_tunnel
tasklist /fi "imagename eq ssh.exe" 2>nul | find /i "ssh.exe" >nul
if errorlevel 1 (
    echo [%date% %time%] Tunel SSH caido. Reiniciando en 5 segundos... >> server_data\server_log.txt
    ping 127.0.0.1 -n 6 >nul
    goto tunnel_loop
)
ping 127.0.0.1 -n 11 >nul
goto wait_tunnel

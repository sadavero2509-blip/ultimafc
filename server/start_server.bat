@echo off
title Futbol Game - Server Console
echo ========================================
echo   FUTBOL GAME - CENTRAL SERVER 2024
echo ========================================
echo.
echo Instalando dependencias necesarias...
pip install flask flask-cors flask-socketio requests python-dotenv
echo.
echo Iniciando servidor...
python app.py
pause

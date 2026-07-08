@echo off
title Detener Servidor - Neo Futbol Arcade
echo ==============================================
echo   Deteniendo Servidor y Tunel SSH...
echo ==============================================
echo.

taskkill /f /im python.exe 2>nul
taskkill /f /im ssh.exe 2>nul

echo.
echo ==============================================
echo   PROCESOS FINALIZADOS
echo ==============================================
echo.
pause

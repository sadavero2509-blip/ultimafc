@echo off
title Actualizador de Ultima FC 27
echo ==============================================
echo   Aplicando actualizacion de Ultima FC 27...
echo ==============================================
timeout /t 2 /nobreak >nul
if exist "_UltimaFC27_update.exe" (
    del /f "UltimaFC27.exe" 2>nul
    rename "_UltimaFC27_update.exe" "UltimaFC27.exe"
    echo Actualizacion aplicada con exito.
    start "" "UltimaFC27.exe"
) else if exist "_NeoFutbolArcade_update.exe" (
    del /f "UltimaFC27.exe" 2>nul
    rename "_NeoFutbolArcade_update.exe" "UltimaFC27.exe"
    echo Actualizacion aplicada con exito.
    start "" "UltimaFC27.exe"
)
exit

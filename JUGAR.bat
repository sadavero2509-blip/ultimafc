@echo off
title Neo Futbol Arcade
echo ==========================================
echo     Neo Futbol Arcade - Iniciando...
echo ==========================================
echo.
cd /d "%~dp0"

IF NOT EXIST .venv (
    echo Instalando entorno virtual por primera vez...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Verificando dependencias...
pip install -r requirements.txt

:start_game
echo Ejecutando juego...
echo.
python main.py

IF %ERRORLEVEL% EQU 99 (
    echo.
    echo ==========================================
    echo   ACTUALIZACION DESCARGADA. REINICIANDO...
    echo ==========================================
    echo.
    timeout /t 2 /nobreak >nul
    goto start_game
) ELSE IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo   ERROR: El juego se cerro inesperadamente
    echo   Codigo de error: %ERRORLEVEL%
    echo ==========================================
    echo.
    pause
) ELSE (
    echo.
    echo Juego cerrado correctamente.
)

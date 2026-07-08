@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
::  DEPLOY AUTOMÁTICO - NeoFutbolArcade
::  Compila, empaqueta, commitea y sube todo.
:: ============================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║   DEPLOY AUTOMATICO - NeoFutbolArcade   ║
echo ╚══════════════════════════════════════════╝
echo.

:: Mensaje de commit (parámetro opcional)
if "%~1"=="" (
    set "COMMIT_MSG=Auto-deploy: recompilacion y actualizacion del ejecutable"
) else (
    set "COMMIT_MSG=%~1"
)

:: ── PASO 1: Verificar sintaxis ──────────────────────
echo [1/5] Verificando sintaxis de archivos Python...
.venv\Scripts\python -m py_compile main.py
if errorlevel 1 (
    echo [ERROR] Error de sintaxis en main.py. Abortando.
    exit /b 1
)
.venv\Scripts\python -m py_compile data\career_manager.py
if errorlevel 1 (
    echo [ERROR] Error de sintaxis en career_manager.py. Abortando.
    exit /b 1
)

:: Verificar todos los archivos de scenes/
for %%f in (scenes\*.py) do (
    .venv\Scripts\python -m py_compile "%%f" 2>nul
    if errorlevel 1 (
        echo [ERROR] Error de sintaxis en %%f. Abortando.
        exit /b 1
    )
)

:: Verificar todos los archivos de systems/
for %%f in (systems\*.py) do (
    .venv\Scripts\python -m py_compile "%%f" 2>nul
    if errorlevel 1 (
        echo [ERROR] Error de sintaxis en %%f. Abortando.
        exit /b 1
    )
)

:: Verificar todos los archivos de entities/
for %%f in (entities\*.py) do (
    .venv\Scripts\python -m py_compile "%%f" 2>nul
    if errorlevel 1 (
        echo [ERROR] Error de sintaxis en %%f. Abortando.
        exit /b 1
    )
)

echo    [OK] Sintaxis verificada correctamente.
echo.

:: ── PASO 2: Compilar ejecutable ─────────────────────
echo [2/5] Compilando NeoFutbolArcade.exe con PyInstaller...
.venv\Scripts\pyinstaller NeoFutbolArcade.spec --noconfirm --clean >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller falló. Abortando.
    exit /b 1
)
echo    [OK] Ejecutable compilado exitosamente.
echo.

:: ── PASO 3: Copiar a carpeta de release ─────────────
echo [3/5] Copiando ejecutable a carpeta de distribución...
copy /Y "dist\NeoFutbolArcade.exe" "dist\NeoFutbolArcade_Release\NeoFutbolArcade.exe" >nul
if errorlevel 1 (
    echo [ERROR] No se pudo copiar el ejecutable. Abortando.
    exit /b 1
)

:: Mostrar tamaño del archivo
for %%A in ("dist\NeoFutbolArcade.exe") do (
    set /a "SIZE_MB=%%~zA / 1048576"
    echo    [OK] NeoFutbolArcade.exe (!SIZE_MB! MB) copiado a Release.
)
echo.

:: ── PASO 4: Git commit ──────────────────────────────
echo [4/5] Realizando commit en Git...
git add -A >nul 2>&1
git commit -m "%COMMIT_MSG%" >nul 2>&1
if errorlevel 1 (
    echo    [INFO] No hay cambios nuevos para commitear.
) else (
    echo    [OK] Commit realizado: %COMMIT_MSG%
)
echo.

:: ── PASO 5: Git push ────────────────────────────────
echo [5/5] Subiendo cambios al repositorio remoto...
git push origin main >nul 2>&1
if errorlevel 1 (
    echo [AVISO] No se pudo hacer push. Puede requerir autenticación manual.
    echo         Ejecuta: git push origin main
) else (
    echo    [OK] Cambios subidos exitosamente a GitHub.
)

echo.
echo ╔══════════════════════════════════════════╗
echo ║   DEPLOY COMPLETADO EXITOSAMENTE        ║
echo ║   Los jugadores recibirán la             ║
echo ║   actualización al reiniciar el juego.   ║
echo ╚══════════════════════════════════════════╝
echo.

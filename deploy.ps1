param(
    [string]$CommitMsg = "Auto-deploy: recompilacion y actualizacion del ejecutable"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "===== DEPLOY AUTOMATICO - NeoFutbolArcade =====" -ForegroundColor Cyan
Write-Host ""

# -- PASO 1: Verificar sintaxis --
Write-Host "[1/5] Verificando sintaxis..." -ForegroundColor Yellow
$pyFiles = Get-ChildItem -Path $root -Recurse -Include "*.py" |
    Where-Object { $_.FullName -notmatch '\\\.venv\\|\\venv\\|\\build\\|\\dist\\|\\server\\|\\__pycache__\\' }

$syntaxOk = $true
foreach ($f in $pyFiles) {
    & "$root\.venv\Scripts\python.exe" -m py_compile $f.FullName 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [ERROR] $($f.Name)" -ForegroundColor Red
        $syntaxOk = $false
    }
}
if (-not $syntaxOk) {
    Write-Host "Abortando por errores de sintaxis." -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Sintaxis verificada." -ForegroundColor Green
Write-Host ""

# -- PASO 2: Compilar ejecutable --
Write-Host "[2/5] Compilando NeoFutbolArcade.exe..." -ForegroundColor Yellow
$env:PYTHONDONTWRITEBYTECODE = "1"
& "$root\.venv\Scripts\pyinstaller.exe" "$root\NeoFutbolArcade.spec" --noconfirm --clean 2>&1 | ForEach-Object { $_.ToString() } | Out-Null
if (-not (Test-Path "$root\dist\NeoFutbolArcade.exe")) {
    Write-Host "   [ERROR] No se genero el ejecutable." -ForegroundColor Red
    exit 1
}
$exeSize = [math]::Round((Get-Item "$root\dist\NeoFutbolArcade.exe").Length / 1MB, 1)
Write-Host "   [OK] Compilado ($exeSize MB)." -ForegroundColor Green
Write-Host ""

# -- PASO 3: Copiar a release --
Write-Host "[3/5] Copiando a carpeta de distribucion..." -ForegroundColor Yellow
Copy-Item -Path "$root\dist\NeoFutbolArcade.exe" -Destination "$root\dist\NeoFutbolArcade_Release\NeoFutbolArcade.exe" -Force

# Sincronizar assets (audio, etc.) al release
if (Test-Path "$root\assets") {
    Copy-Item -Path "$root\assets" -Destination "$root\dist\NeoFutbolArcade_Release\" -Recurse -Force
}
# Sincronizar data (rosters, equipos, etc.) al release
if (Test-Path "$root\data") {
    Copy-Item -Path "$root\data" -Destination "$root\dist\NeoFutbolArcade_Release\" -Recurse -Force
    # Limpiar __pycache__ del release
    Get-ChildItem -Path "$root\dist\NeoFutbolArcade_Release\data" -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
# Sincronizar settings.py al release
if (Test-Path "$root\settings.py") {
    Copy-Item -Path "$root\settings.py" -Destination "$root\dist\NeoFutbolArcade_Release\settings.py" -Force
}

Write-Host "   [OK] Copiado a NeoFutbolArcade_Release." -ForegroundColor Green
Write-Host ""

# -- PASO 3b: Sincronizar instalacion local (AppData) --
$localInstall = "$env:LOCALAPPDATA\Programs\NeoFutbol Arcade"
if (Test-Path $localInstall) {
    Write-Host "[3b] Sincronizando instalacion local..." -ForegroundColor Yellow
    Copy-Item -Path "$root\dist\NeoFutbolArcade.exe" -Destination "$localInstall\NeoFutbolArcade.exe" -Force
    if (Test-Path "$root\assets") {
        Copy-Item -Path "$root\assets" -Destination "$localInstall\" -Recurse -Force
    }
    if (Test-Path "$root\data") {
        Copy-Item -Path "$root\data" -Destination "$localInstall\" -Recurse -Force
        Get-ChildItem -Path "$localInstall\data" -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
    foreach ($f in @("settings.py", "server_cfg.py", "server_config.json")) {
        if (Test-Path "$root\$f") {
            Copy-Item -Path "$root\$f" -Destination "$localInstall\$f" -Force
        }
    }
    Write-Host "   [OK] Instalacion local actualizada ($localInstall)." -ForegroundColor Green
    Write-Host ""
}

# -- PASO 4: Git commit --
Write-Host "[4/5] Git commit..." -ForegroundColor Yellow
Set-Location $root
git add -A 2>&1 | Out-Null
$commitOut = git commit -m $CommitMsg 2>&1 | Out-String
if ($commitOut -match "nothing to commit") {
    Write-Host "   [INFO] No hay cambios nuevos." -ForegroundColor DarkYellow
} else {
    Write-Host "   [OK] Commit realizado." -ForegroundColor Green
}
Write-Host ""

# -- PASO 5: Git push --
Write-Host "[5/5] Git push..." -ForegroundColor Yellow
git push origin main 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [AVISO] Push fallo. Ejecuta: git push origin main" -ForegroundColor DarkYellow
} else {
    Write-Host "   [OK] Subido a GitHub." -ForegroundColor Green
}

Write-Host ""
Write-Host "===== DEPLOY COMPLETADO =====" -ForegroundColor Cyan
Write-Host "Los jugadores recibiran la actualizacion al reiniciar el juego."
Write-Host ""

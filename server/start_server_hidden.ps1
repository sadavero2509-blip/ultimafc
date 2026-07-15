# ============================================================
#  ULTIMA FC - Servidor Oculto con Auto-Reinicio
#  Este script mantiene el servidor vivo indefinidamente.
#  Si el proceso muere (crash, error de red, etc.), se reinicia
#  automáticamente tras una breve pausa.
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

# --- Configuración ---
$ServerDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ServerDir
$PythonExe  = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AppScript  = Join-Path $ServerDir "app.py"
$LogFile    = Join-Path $ServerDir "server_data\server_log.txt"
$RestartDelay = 5  # Segundos entre reinicios

# Fallback: si no existe el venv, buscar python del sistema
if (-not (Test-Path $PythonExe)) {
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) {
        Add-Content $LogFile "[$(Get-Date)] ERROR FATAL: No se encontro Python."
        exit 1
    }
}

# Asegurar que el directorio de logs exista
$logDir = Split-Path -Parent $LogFile
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# --- Función: verificar si ya hay una instancia corriendo ---
function Test-ServerRunning {
    $procs = Get-Process -Name "python*" -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue).CommandLine
            if ($cmdLine -and $cmdLine -match "app\.py") {
                return $true
            }
        } catch {}
    }
    return $false
}

# --- Evitar instancias duplicadas ---
if (Test-ServerRunning) {
    Add-Content $LogFile "[$(Get-Date)] Servidor ya en ejecucion. Saliendo."
    exit 0
}

Add-Content $LogFile "[$(Get-Date)] ====== INICIO DEL SERVIDOR (PID guardián: $PID) ======"

# --- Loop principal de resiliencia ---
while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content $LogFile "[$timestamp] Iniciando servidor..."

    try {
        # Iniciar el servidor y esperar a que termine (crash o cierre)
        $proc = Start-Process -FilePath $PythonExe -ArgumentList "`"$AppScript`"" `
            -WorkingDirectory $ServerDir -WindowStyle Hidden -PassThru -NoNewWindow

        Add-Content $LogFile "[$timestamp] Servidor iniciado (PID: $($proc.Id))"

        # Esperar a que el proceso termine (bloqueante)
        $proc.WaitForExit()

        $exitCode = $proc.ExitCode
        $exitTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content $LogFile "[$exitTime] Servidor detenido (código: $exitCode)"

    } catch {
        $errTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content $LogFile "[$errTime] ERROR al iniciar servidor: $($_.Exception.Message)"
    }

    # Pausa antes del reinicio automático
    Add-Content $LogFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Reiniciando en $RestartDelay segundos..."
    Start-Sleep -Seconds $RestartDelay
}

# ============================================================
#  ULTIMA FC - Servidor Guardián Resiliente
#  Mantiene vivos tanto el servidor Flask como el túnel SSH.
#  Si se pierde la conexión a Internet o se cierra alguno,
#  los reinicia automáticamente y actualiza la URL en el cliente.
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

# --- Configuración ---
$ServerDir   = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ServerDir
$PythonExe   = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AppScript   = Join-Path $ServerDir "app.py"
$LogFile     = Join-Path $ServerDir "server_data\server_log.txt"
$TunnelLog   = Join-Path $ProjectRoot "tunnel.log"
$TunnelErr   = Join-Path $ProjectRoot "tunnel_err.log"
$UpdateScript = Join-Path $ProjectRoot "scratch\update_tunnel_url.py"
$RestartDelay = 5  # Segundos de espera

# Fallback para Python
if (-not (Test-Path $PythonExe)) {
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) {
        Add-Content $LogFile "[$(Get-Date)] ERROR FATAL: No se encontró Python."
        exit 1
    }
}

# Asegurar directorios
$logDir = Split-Path -Parent $LogFile
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

Add-Content $LogFile "[$(Get-Date)] ====== INICIANDO GUARDIÁN DEL SERVIDOR (PID: $PID) ======"

# --- Limpieza Inicial ---
Add-Content $LogFile "[$(Get-Date)] Limpiando procesos de servidor/ssh previos..."
Get-Process -Name "ssh" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -match "FutbolGame" } | Stop-Process -Force
Start-Sleep -Seconds 1

# Variables de estado de procesos
$AppProcess = $null
$SshProcess = $null

# Loop principal de resiliencia
while ($true) {
    # --- 1. Verificar y mantener vivo Flask (app.py) ---
    $needStartApp = $false
    if ($AppProcess -eq $null) {
        $needStartApp = $true
    } else {
        if ($AppProcess.HasExited) {
            $needStartApp = $true
        }
    }

    if ($needStartApp) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content $LogFile "[$timestamp] Iniciando proceso del servidor Flask..."
        try {
            $AppProcess = Start-Process -FilePath $PythonExe -ArgumentList "`"$AppScript`"" `
                -WorkingDirectory $ServerDir -WindowStyle Hidden -PassThru
            Add-Content $LogFile "[$timestamp] Servidor Flask iniciado (PID: $($AppProcess.Id))"
        } catch {
            Add-Content $LogFile "[$timestamp] ERROR iniciando Flask: $($_.Exception.Message)"
            $AppProcess = $null
        }
    }

    # --- 2. Verificar y mantener vivo el túnel SSH ---
    $needStartSsh = $false
    if ($SshProcess -eq $null) {
        $needStartSsh = $true
    } else {
        if ($SshProcess.HasExited) {
            $needStartSsh = $true
        }
    }

    if ($needStartSsh) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content $LogFile "[$timestamp] Túnel SSH caído o no iniciado. Iniciando conexión con Serveo..."
        
        # Eliminar logs viejos para evitar falsos positivos
        if (Test-Path $TunnelLog) { Remove-Item $TunnelLog -Force }
        if (Test-Path $TunnelErr) { Remove-Item $TunnelErr -Force }

        # Buscar clave SSH si existe
        $SshKeyOpt = ""
        $userProfile = [System.Environment]::GetFolderPath('UserProfile')
        if (Test-Path "$userProfile\FutbolGame") {
            $SshKeyOpt = "$userProfile\FutbolGame"
        }

        # Preparar argumentos como array para evitar fallos de parseo
        $SshArgs = @()
        if ($SshKeyOpt -ne "") {
            $SshArgs += "-i"
            $SshArgs += $SshKeyOpt
        }
        $SshArgs += "-o"
        $SshArgs += "StrictHostKeyChecking=no"
        $SshArgs += "-o"
        $SshArgs += "ExitOnForwardFailure=yes"
        $SshArgs += "-R"
        $SshArgs += "neofutbol-sadav:80:127.0.0.1:25565"
        $SshArgs += "serveo.net"

        try {
            # Iniciar SSH redirigiendo stdout/stderr a ficheros separados
            $SshProcess = Start-Process -FilePath "ssh.exe" `
                -ArgumentList $SshArgs -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru `
                -RedirectStandardOutput $TunnelLog -RedirectStandardError $TunnelErr
            
            Add-Content $LogFile "[$timestamp] Proceso SSH lanzado (PID: $($SshProcess.Id))"

            # Esperar a que se asigne la URL y actualizar
            Start-Sleep -Seconds 6
            if (Test-Path $UpdateScript) {
                Add-Content $LogFile "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Ejecutando actualizador de URL..."
                & $PythonExe $UpdateScript | Out-Null
            }
        } catch {
            Add-Content $LogFile "[$timestamp] ERROR iniciando túnel SSH: $($_.Exception.Message)"
            $SshProcess = $null
        }
    }

    # Pausa antes del siguiente chequeo
    Start-Sleep -Seconds $RestartDelay
}

# Management panel launcher: starts the backend (if it is not running yet), installs the panel's packages the
# first time, then runs the React panel (management/) and opens it in the browser at http://localhost:5173.
# Closing the panel (Ctrl+C) also stops the backend it started.
#
# Usage (from the repo root):
#   .\run-management.ps1             # backend + panel
#   .\run-management.ps1 -NoBrowser  # does not open the browser
param(
    [switch]$NoBrowser,
    [int]$Port = 8001,
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$panel = Join-Path $root "management"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js (https://nodejs.org) and open a new terminal."
}

# Prefer the project's virtualenv; fall back to the python on PATH
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

function Test-Port([int]$port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.ConnectAsync("127.0.0.1", $port).Wait(500) -and $client.Connected
    } catch { $false } finally { $client.Dispose() }
}

# The panel needs port 5173 (management/vite.config.js, strictPort): say who holds it instead of Vite's raw error
$panelPort = 5173
$holder = Get-NetTCPConnection -LocalPort $panelPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($holder) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($holder.OwningProcess)"
    Write-Host "Port $panelPort is already in use by process $($holder.OwningProcess) ($($process.Name))." -ForegroundColor Red
    Write-Host "  $($process.CommandLine)" -ForegroundColor DarkGray
    Write-Host "If it is an old panel, open http://localhost:$panelPort or stop it with: Stop-Process -Id $($holder.OwningProcess)" -ForegroundColor Yellow
    exit 1
}

$backend = $null
if (Test-Port $Port) {
    Write-Host "Backend already running on port $Port, reusing it." -ForegroundColor Yellow
} else {
    Write-Host "Starting the backend on port $Port..." -ForegroundColor Cyan
    # Separate window so the uvicorn log stays readable
    $backend = Start-Process -FilePath $python -ArgumentList "main.py" `
        -WorkingDirectory (Join-Path $root "backend") -PassThru

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not (Test-Port $Port)) {
        if ($backend.HasExited) { throw "The backend exited during startup (code $($backend.ExitCode))." }
        if ((Get-Date) -gt $deadline) {
            Stop-Process -Id $backend.Id -Force
            throw "The backend did not answer on port $Port within $TimeoutSeconds s."
        }
        Start-Sleep -Milliseconds 300
    }
    Write-Host "Backend is up." -ForegroundColor Green
}

Push-Location $panel
try {
    if (-not (Test-Path (Join-Path $panel "node_modules"))) {
        Write-Host "Installing the panel's packages (first run)..." -ForegroundColor Cyan
        npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
    }
    Write-Host "Starting the management panel on http://localhost:5173 ..." -ForegroundColor Cyan
    if ($NoBrowser) { npm run dev } else { npm run dev -- --open }
} finally {
    Pop-Location
    if ($backend -and -not $backend.HasExited) {
        Write-Host "Stopping the backend..." -ForegroundColor Cyan
        # /T also kills uvicorn's child processes
        taskkill /PID $backend.Id /T /F | Out-Null
    }
}

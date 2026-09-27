$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonExe = Join-Path $projectRoot 'backend/.venv/Scripts/python.exe'
$logDir = Join-Path $projectRoot '.local'

function Test-LocalPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try { $client.Connect('127.0.0.1', $Port); return $true }
    catch { return $false }
    finally { $client.Dispose() }
}

function Wait-Http([string]$Url) {
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Seconds 1
    }
    throw "Service unavailable: $Url. Check logs in $logDir"
}

if (-not (Test-Path $pythonExe)) { throw 'Install backend dependencies first. See README.md.' }
if (-not (Test-Path (Join-Path $projectRoot 'backend/.env'))) { throw 'Initialize the database first. See README.md.' }
if (-not (Test-Path (Join-Path $projectRoot 'frontend/node_modules/vite/bin/vite.js'))) { throw 'Install frontend dependencies first. See README.md.' }
New-Item -ItemType Directory -Force $logDir | Out-Null

if (-not (Test-LocalPort 3306)) {
    & $pythonExe (Join-Path $projectRoot 'database/local_mysql.py') start
    if ($LASTEXITCODE -ne 0) { throw 'MySQL could not start.' }
}
if (-not (Test-LocalPort 8000)) {
    Start-Process -FilePath $pythonExe -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'backend.stdout.log') -RedirectStandardError (Join-Path $logDir 'backend.stderr.log') | Out-Null
}
Wait-Http 'http://127.0.0.1:8000/api/health'
if (-not (Test-LocalPort 5173)) {
    Start-Process -FilePath (Get-Command node.exe).Source -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'frontend.stdout.log') -RedirectStandardError (Join-Path $logDir 'frontend.stderr.log') | Out-Null
}
Wait-Http 'http://127.0.0.1:5173/api/health'
Write-Host 'CampusLink is ready: http://127.0.0.1:5173'
Write-Host 'API documentation: http://127.0.0.1:8000/docs'
Write-Host 'Services run in the background. Closing this window does not stop them.'

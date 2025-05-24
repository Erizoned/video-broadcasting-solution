Write-Host "=== Starting services ===" -ForegroundColor Green

# 1. Run nginx-rtmp via Docker
Write-Host "[1/4] Starting nginx-rtmp container..." -ForegroundColor Cyan
docker rm -f nginx-rtmp | Out-Null
docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp | Out-Null

# 2. Start uvicorn (FastAPI backend)
Write-Host "[2/4] Starting uvicorn..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath
Start-Process powershell -ArgumentList "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -NoNewWindow

# 3. Start React frontend (npm start in /front)
Write-Host "[3/4] Starting React frontend (npm start)..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "front"
Set-Location $frontendPath
Start-Process powershell -ArgumentList "npm start" -WorkingDirectory $frontendPath

# 4. Restart MediaMTX (docker compose down/up)
Write-Host "[4/4] Restarting MediaMTX stack..." -ForegroundColor Cyan
$mtPath = Join-Path $PSScriptRoot "mt"
Set-Location $mtPath
docker compose down | Out-Null
docker compose up -d | Out-Null

Write-Host "=== All services started ===" -ForegroundColor Green
Pause

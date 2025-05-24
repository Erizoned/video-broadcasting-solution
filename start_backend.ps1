Write-Host "=== Starting services ===" -ForegroundColor Green

# 1. Run nginx-rtmp via Docker
Write-Host "[1/5] Starting nginx-rtmp container..." -ForegroundColor Cyan
docker rm -f nginx-rtmp | Out-Null
docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp | Out-Null

# 2. Start uvicorn (FastAPI backend)
Write-Host "[2/5] Starting uvicorn..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath
Start-Process powershell -ArgumentList "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -NoNewWindow

# 4. Restart MediaMTX (docker compose down/up)
Write-Host "[4/5] Restarting MediaMTX stack..." -ForegroundColor Cyan
$mtPath = Join-Path $PSScriptRoot "mt"
Set-Location $mtPath
docker compose down | Out-Null
docker compose up -d | Out-Null

Write-Host "=== All services started ===" -ForegroundColor Green
Pause
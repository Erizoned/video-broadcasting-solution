Write-Host "=== Starting backend ===" -ForegroundColor Green

# Path to backend
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

# 1. Start uvicorn
Write-Host "[1/5] Starting uvicorn..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -NoNewWindow

# 2. Run nginx-rtmp via Docker
Write-Host "[2/5] Starting nginx-rtmp container..." -ForegroundColor Cyan
docker rm -f nginx-rtmp | Out-Null
docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp | Out-Null

# 3. Check and start stream
$videoPath = Join-Path $env:USERPROFILE "Documents\Github\video-broadcasting-solution\sample1.mp4"
if (Test-Path $videoPath) {
    Write-Host "[3/5] Starting stream with video: $videoPath" -ForegroundColor Cyan
    .\stream.bat "$videoPath" "drone"
} else {
    Write-Host "[ERROR] Video file not found at: $videoPath" -ForegroundColor Red
}

# 4. Run docker compose
$mtPath = Join-Path $PSScriptRoot "mt"
Set-Location $mtPath
Write-Host "[4/5] Starting docker compose..." -ForegroundColor Cyan
docker compose up -d | Out-Null

Write-Host "=== All services started ===" -ForegroundColor Green
Pause

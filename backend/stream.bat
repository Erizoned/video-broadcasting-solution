@echo off
set VIDEO=%~1
set KEY=%~2
if "%VIDEO%"=="" (
  echo Usage: stream.bat path\to\video.mp4 [stream_key]
  exit /b 1
)
if "%KEY%"=="" set KEY=drone
ffmpeg -re -stream_loop -1 -i "%VIDEO%" -c copy -f flv "rtmp://127.0.0.1/live/%KEY%"

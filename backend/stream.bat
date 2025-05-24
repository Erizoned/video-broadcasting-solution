@echo off
set VIDEO=%~1
set KEY=%~2

if "%VIDEO%"=="" (
echo Usage: stream.bat path\to\video.mp4 [stream_key]
exit /b 1
)
if "%KEY%"=="" set KEY=drone

echo Starting stream for video: %VIDEO% with key: %KEY%

echo FPS set to 15

ffmpeg -re -stream_loop -1 -i "%VIDEO%" ^
-vf "fps=15" ^
-c:v libx264 -preset veryfast -tune zerolatency ^
-c:a aac -ar 44100 -b:a 128k ^
-f flv "rtmp://127.0.0.1/live/%KEY%"
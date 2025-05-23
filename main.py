from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import Dict

app = FastAPI()

class StreamRequest(BaseModel):
    input_rtmp: str       # RTMP-адрес источника
    stream_name: str      # Уникальное имя для RTSP-потока

# Хранилище активных FFmpeg-процессов
streams: Dict[str, subprocess.Popen] = {}

@app.post("/convert")
async def start_conversion(req: StreamRequest):
    # Проверяем, что поток с таким именем ещё не запущен
    if req.stream_name in streams:
        raise HTTPException(status_code=400, detail="Stream already running")

    # RTSP-адрес, по которому будем отдавать поток
    rtsp_url = f"rtsp://localhost:8554/{req.stream_name}"

    # Команда FFmpeg: читаем RTMP, копируем кодеки, отдаём RTSP
    cmd = [
        "ffmpeg", "-i", req.input_rtmp,
        "-c", "copy", "-f", "rtsp", rtsp_url
    ]

    # Запускаем FFmpeg в фоновом режиме
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    streams[req.stream_name] = proc

    return {"rtsp_url": rtsp_url}

@app.delete("/convert/{stream_name}")
async def stop_conversion(stream_name: str):
    # Останавливаем процесс по имени потока
    proc = streams.get(stream_name)
    if not proc:
        raise HTTPException(status_code=404, detail="Stream not found")
    proc.terminate()
    proc.wait()
    del streams[stream_name]
    return {"detail": "stopped"}
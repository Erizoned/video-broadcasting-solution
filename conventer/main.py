from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
from typing import Dict

app = FastAPI(
    title="RTMP→RTSP Converter",
    description="REST API для конвертации RTMP-потока в RTSP-ссылку",
)

# Словарь для хранения запущенных процессов ffmpeg
processes: Dict[str, subprocess.Popen] = {}

class StreamRequest(BaseModel):
    rtmp_url: str

class StreamInfo(BaseModel):
    id: str
    rtsp_url: str

@app.post("/streams", response_model=StreamInfo)
def create_stream(request: StreamRequest):
    """
    Запустить конвертацию RTMP->RTSP.
    Возвращает ID и RTSP URL.
    """
    # Генерируем уникальный ID и имя потока
    stream_id = str(uuid.uuid4())
    stream_name = f"stream_{stream_id}"
    rtsp_url = f"rtsp://0.0.0.0:8554/{stream_name}"

    # Команда ffmpeg: слушать клиентские подключения (?listen)
    cmd = [
        "ffmpeg",
        "-i", request.rtmp_url,
        "-c", "copy",
        "-f", "rtsp",
        f"{rtsp_url}?listen"
    ]

    # Запускаем процесс в фоне
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes[stream_id] = process

    return StreamInfo(id=stream_id, rtsp_url=rtsp_url)

@app.delete("/streams/{stream_id}")
def stop_stream(stream_id: str):
    """
    Остановить конвертацию по ID.
    """
    process = processes.get(stream_id)
    if not process:
        raise HTTPException(status_code=404, detail="Stream not found")

    process.kill()
    del processes[stream_id]
    return {"detail": f"Stream {stream_id} stopped"}

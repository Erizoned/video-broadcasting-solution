from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
import subprocess

app = FastAPI(title="Drone Stream Simulator")

# храним процессы по ключу стрима
processes: Dict[str, subprocess.Popen] = {}

class StreamRequest(BaseModel):
    video_path: str
    stream_key: str = "drone"
    rtmp_url: str = "rtmp://localhost/live"

@app.post("/stream/start")
async def start_stream(req: StreamRequest):
    key = req.stream_key
    if key in processes and processes[key].poll() is None:
        raise HTTPException(status_code=409, detail=f"Stream '{key}' уже запущен")
    cmd = [
        "ffmpeg",
        "-re",                  # real-time эмуляция
        "-stream_loop", "-1",   # зациклить
        "-i", req.video_path,
        "-c", "copy",
        "-f", "flv",
        f"{req.rtmp_url}/{key}"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg не найден в PATH")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    processes[key] = proc
    return {"message": f"Stream '{key}' запущен на {req.rtmp_url}/{key}"}

@app.post("/stream/stop")
async def stop_stream(stream_key: str = Query(..., description="ключ потока")):
    proc = processes.get(stream_key)
    if not proc or proc.poll() is not None:
        raise HTTPException(status_code=404, detail=f"Stream '{stream_key}' не запущен")
    proc.terminate()
    proc.wait(timeout=5)
    processes.pop(stream_key, None)
    return {"message": f"Stream '{stream_key}' остановлен"}

@app.get("/stream/status")
async def stream_status(stream_key: str = Query(..., description="ключ потока")):
    proc = processes.get(stream_key)
    if proc and proc.poll() is None:
        return {"stream_key": stream_key, "status": "running"}
    return {"stream_key": stream_key, "status": "stopped"}

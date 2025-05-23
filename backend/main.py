from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import Dict

app = FastAPI()

class StreamRequest(BaseModel):
    input_rtmp: str
    stream_name: str

streams: Dict[str, subprocess.Popen] = {}

RTSP_HOST = "rtsp-server"
RTSP_PORT = 8554

@app.post("/convert")
async def start_conversion(req: StreamRequest):
    if req.stream_name in streams:
        raise HTTPException(400, "Stream already running")

    container_url = f"rtsp://{RTSP_HOST}:{RTSP_PORT}/{req.stream_name}"
    public_url = f"rtsp://localhost:{RTSP_PORT}/{req.stream_name}"

    cmd = [
        "ffmpeg", "-rtsp_transport", "tcp", "-i", req.input_rtmp,
        "-c", "copy", "-f", "rtsp", container_url
    ]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    streams[req.stream_name] = proc

    return {"rtsp_url": public_url}

@app.delete("/convert/{stream_name}")
async def stop_conversion(stream_name: str):
    proc = streams.get(stream_name)
    if not proc:
        raise HTTPException(404, "Stream not found")
    proc.terminate()
    proc.wait()
    streams.pop(stream_name, None)
    return {"detail": "stopped"}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import Dict

app = FastAPI()

class StreamRequest(BaseModel):
    input_rtmp: str       # RTMP source URL
    stream_name: str      # Unique name for RTSP stream

# Store active FFmpeg processes
streams: Dict[str, subprocess.Popen] = {}

# Environment or default RTSP server hostname in Docker network
RTSP_SERVER_HOST = "rtsp-server"  # service name in docker-compose
RTSP_SERVER_PORT = 8554

@app.post("/convert")
async def start_conversion(req: StreamRequest):
    if req.stream_name in streams:
        raise HTTPException(status_code=400, detail="Stream already running")

    # Container-internal RTSP URL for publishing
    container_rtsp_url = f"rtsp://{RTSP_SERVER_HOST}:{RTSP_SERVER_PORT}/{req.stream_name}"
    # Public RTSP URL returned to client
    public_rtsp_url = f"rtsp://localhost:{RTSP_SERVER_PORT}/{req.stream_name}"

    # Spawn FFmpeg: read RTMP, copy codecs, publish to RTSP
    cmd = [
        "ffmpeg", "-rtsp_transport", "tcp", "-i", req.input_rtmp,
        "-c", "copy", "-f", "rtsp", container_rtsp_url
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg not found in container")

    streams[req.stream_name] = proc
    return {"rtsp_url": public_rtsp_url}

@app.delete("/convert/{stream_name}")
async def stop_conversion(stream_name: str):
    proc = streams.get(stream_name)
    if not proc:
        raise HTTPException(status_code=404, detail="Stream not found")
    proc.terminate()
    proc.wait()
    del streams[stream_name]
    return {"detail": "stopped"}

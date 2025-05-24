from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import os
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

# ----------------------------------------------
# Streaming service for RTMP generation below
# ----------------------------------------------
processes: Dict[str, subprocess.Popen] = {}

class PublishRequest(BaseModel):
    video_path: str
    stream_key: str = "drone"
    rtmp_url: str = "rtmp://localhost/live"

@app.post("/stream/start")
async def start_stream(req: PublishRequest):
    key = req.stream_key
    # Prevent duplicate streams
    if key in processes and processes[key].poll() is None:
        raise HTTPException(status_code=409, detail=f"Stream '{key}' already running")

    # Build ffmpeg command to push to RTMP
    ffmpeg_cmd = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", req.video_path,
        "-c", "copy",
        "-f", "flv",
        f"{req.rtmp_url}/{key}"
    ]
    try:
        proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg not found in PATH")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Track ffmpeg process
    processes[key] = proc

    # Also invoke the batch file to ensure Windows compatibility
    # Assume 'stream.bat' is in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_path = os.path.join(script_dir, 'stream.bat')
    try:
        bat_proc = subprocess.Popen(
            ['cmd', '/c', batch_path, req.video_path, req.stream_key],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes[f"{key}_bat"] = bat_proc
    except Exception as e:
        # If batch fails, we still keep ffmpeg; report the error
        raise HTTPException(status_code=500, detail=f"Failed to start batch script: {e}")

    return {"message": f"Stream '{key}' started at {req.rtmp_url}/{key}"}

@app.delete("/stream/stop")
async def stop_stream(stream_key: str = Query(..., description="stream key")):
    proc = processes.get(stream_key)
    if not proc or proc.poll() is not None:
        raise HTTPException(status_code=404, detail=f"Stream '{stream_key}' not running")
    proc.terminate()
    proc.wait(timeout=5)
    processes.pop(stream_key, None)

    # Stop batch process too
    bat_key = f"{stream_key}_bat"
    bat_proc = processes.get(bat_key)
    if bat_proc and bat_proc.poll() is None:
        bat_proc.terminate()
        bat_proc.wait(timeout=5)
        processes.pop(bat_key, None)

    return {"message": f"Stream '{stream_key}' stopped"}

@app.get("/stream/status")
async def stream_status(stream_key: str = Query(..., description="stream key")):
    proc = processes.get(stream_key)
    status = "running" if proc and proc.poll() is None else "stopped"
    return {"stream_key": stream_key, "status": status}

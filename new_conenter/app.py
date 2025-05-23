# wrapper.py
# Python service wrapper to proxy RTMP streams to RTSP via FFmpeg and mediamtx
# Requirements: Python 3.7+, FastAPI, Uvicorn, FFmpeg installed and in PATH

import os
import signal
import subprocess
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()
# Keep track of running FFmpeg processes per stream ID
processes = {}

# Configuration via environment variables
RTMP_HOST = os.getenv("RTMP_HOST", "localhost")
RTMP_PORT = os.getenv("RTMP_PORT", "1940")
RTSP_PORT = os.getenv("RTSP_PORT", "1940")
HTTP_PORT = int(os.getenv("HTTP_PORT", 8000))


def get_urls(stream_id: str):
    """
    Build input and output URLs for given stream ID.
    """
    input_url = f"rtmp://{RTMP_HOST}:{RTMP_PORT}/live/{stream_id}"
    output_url = f"rtsp://{RTMP_HOST}:{RTSP_PORT}/live/{stream_id}"
    return input_url, output_url


@app.post("/streams/{stream_id}")
async def start_stream(stream_id: str):
    """
    Start proxying an RTMP stream to RTSP for the given stream ID.
    """
    if stream_id in processes:
        raise HTTPException(status_code=400, detail="Stream already running")

    in_url, out_url = get_urls(stream_id)
    cmd = [
        "ffmpeg",
        "-i", in_url,
        "-c:v", "copy",        # copy video codec
        "-c:a", "aac",         # encode audio to AAC
        "-f", "rtsp",
        out_url
    ]
    # Start ffmpeg in its own process group to allow clean termination
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    processes[stream_id] = proc
    return {"message": f"Started stream '{stream_id}'", "pid": proc.pid}


@app.delete("/streams/{stream_id}")
async def stop_stream(stream_id: str):
    """
    Stop the proxy FFmpeg process for the given stream ID.
    """
    proc = processes.get(stream_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Terminate the entire process group
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
    del processes[stream_id]
    return {"message": f"Stopped stream '{stream_id}'"}


@app.get("/streams")
async def list_streams():
    """
    List all currently running stream proxies.
    """
    return {"streams": list(processes.keys())}


if __name__ == "__main__":
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)

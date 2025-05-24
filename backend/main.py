from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import os, time
from typing import Dict

app = FastAPI()
processes: Dict[str, subprocess.Popen] = {}

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
    video = req.video_path
    rtmp_target = f"{req.rtmp_url.rstrip('/')}/{key}"

    # 1. Prevent duplicate streams
    if key in processes and processes[key].poll() is None:
        raise HTTPException(409, f"Stream '{key}' уже запущен")

    # 2. Ensure input file exists
    if not os.path.isfile(video):
        raise HTTPException(400, f"Видео не найдено: {video}")

    # 3. Launch ffmpeg
    ffmpeg_cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1",
        "-i", video, "-c", "copy", "-f", "flv", rtmp_target
    ]
    print(f"[START] FFmpeg command: {' '.join(ffmpeg_cmd)}")
    try:
        proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(500, "ffmpeg не найден в PATH")
    except Exception as e:
        raise HTTPException(500, f"Ошибка запуска ffmpeg: {e}")

    # brief pause and health check
    time.sleep(0.5)
    if proc.poll() is not None:
        err = proc.stderr.read().decode(errors='ignore').strip()
        raise HTTPException(500, f"ffmpeg завершился сразу: {err or 'без вывода'}")
    processes[key] = proc
    print(f"[START] FFmpeg запущен (PID={proc.pid}) для потока '{key}'")

    # 4. Launch batch script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_path = os.path.join(script_dir, "stream.bat")
    if not os.path.isfile(batch_path):
        raise HTTPException(500, f"stream.bat не найден по пути {batch_path}")

    bat_cmd = ["cmd", "/c", batch_path, video, key]
    print(f"[START] Batch command: {' '.join(bat_cmd)} (cwd={script_dir})")
    try:
        bat_proc = subprocess.Popen(
            bat_cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        proc.terminate()
        raise HTTPException(500, f"Не удалось запустить stream.bat: {e}")

    processes[f"{key}_bat"] = bat_proc

    # 5. Wait 2 seconds then capture last 5 lines of batch output
    time.sleep(2)
    out = bat_proc.stdout.read() or b""
    err = bat_proc.stderr.read() or b""
    combined = (out + err).decode(errors='ignore').splitlines()
    last_lines = combined[-5:]

    print(f"[START] stream.bat (PID={bat_proc.pid}) запущен для потока '{key}'")
    return {
        "message": f"Stream '{key}' запущен на {rtmp_target}",
        "batch_logs": last_lines
    }

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

import re
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import subprocess
import tempfile
import os

app = FastAPI()

# Точка добавления путей в MediaMTX
MEDIA_MTX_API = "http://localhost:9997/v3/config/paths/add"

class StreamRegistration(BaseModel):
    rtmp_source: str  # теперь передаем полный RTMP URL

@app.post("/register-stream")
async def register_stream(req: StreamRegistration):
    # 1. Берем RTMP URL из запроса
    rtmp_source = req.rtmp_source.strip()
    m = re.match(r"^rtmp://[^/]+/live/([^/]+)$", rtmp_source)
    if not m:
        raise HTTPException(400, detail="rtmp_source должен быть вида rtmp://<host>/live/<stream_key>")
    stream_key = m.group(1)

    # 2. Формируем имя пути и RTSP URL
    path_name = f"live/{stream_key}"
    rtsp_url = f"rtsp://localhost:8554/{path_name}"

    # 3. Готовим тело запроса к MediaMTX
    payload = {
        "source": rtmp_source,
        "sourceOnDemand": True
    }

    # 4. Отправляем запрос на добавление пути
    url = f"{MEDIA_MTX_API}/{path_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)

    # 5. Логгируем и обрабатываем ошибку
    if resp.status_code != 200:
        print(f"[ERROR] MediaMTX registration failed. URL: {url}, Status: {resp.status_code}, Response: {resp.text}")
        raise HTTPException(
            500,
            detail=f"Ошибка регистрации в MediaMTX: {resp.status_code} {resp.text}"
        )

    # 6. Успех
    return {
        "rtmp_source": rtmp_source,
        "rtsp_url": rtsp_url,
        "status": "registered"
    }

@app.get("/streams/{stream_key}")
async def get_stream_info(stream_key: str):
    """
    Get status and stats for a specific stream_key.
    """
    path_name = f"live/{stream_key}"
    url = f"http://localhost:9997/v3/paths/get/{path_name}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code == 404:
        raise HTTPException(404, detail=f"Stream '{stream_key}' not found")
    if resp.status_code != 200:
        # log full response
        print(f"[ERROR] MediaMTX GET failed. URL: {url}, Status: {resp.status_code}, Body: {resp.text}")
        raise HTTPException(500, detail=f"Error fetching stream info: {resp.status_code}")

    info = resp.json()
    return {
        "stream_key": stream_key,
        "status": "running" if info.get("ready") else "stopped",
        "ready_time": info.get("readyTime"),
        "bytes_received": info.get("bytesReceived"),
        "bytes_sent": info.get("bytesSent"),
        "readers": info.get("readers"),
        "tracks": info.get("tracks"),
    }

@app.get("/streams")
async def list_streams():
    """
    Return a list of all registered RTSP streams with basic stats.
    """
    url = "http://localhost:9997/v3/paths/list"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        print(f"[ERROR] MediaMTX list failed. URL: {url}, "
              f"Status: {resp.status_code}, Body: {resp.text}")
        raise HTTPException(500, detail="Ошибка получения списка стримов")

    data = resp.json()
    items = data.get("items", [])
    streams = []
    for item in items:
        name = item.get("name", "")
        # ожидаем формат "live/<stream_key>"
        stream_key = name.split("/", 1)[1] if "/" in name else name
        streams.append({
            "stream_key": stream_key,
            "status": "running" if item.get("ready") else "stopped",
            "ready_time": item.get("readyTime"),
            "bytes_received": item.get("bytesReceived"),
            "bytes_sent": item.get("bytesSent"),
            "readers_count": len(item.get("readers", [])),
            "tracks": item.get("tracks"),
        })

    return {"streams": streams}

@app.get("/health")
async def health():
    """
    Проверяет доступность MediaMTX.
    Возвращает 200 OK, если MediaMTX отвечает, иначе 503.
    """
    url = "http://localhost:9997/v3/paths/list"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            return {"status": "ok"}
        else:
            # MediaMTX отвечает, но с ошибкой
            raise HTTPException(
                status_code=503,
                detail=f"MediaMTX unhealthy: {resp.status_code}"
            )
    except httpx.RequestError as e:
        # Не смогли достучаться до MediaMTX
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach MediaMTX: {e}"
        )
    

# Чтобы грузить превью и ласт 5 секунд клип

@app.get("/streams/{stream_key}/preview")
async def preview(stream_key: str):
    rtsp = f"rtsp://localhost:8554/live/{stream_key}"
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp", "-i", rtsp,
        "-t", "5",
        "-c", "copy",
        "-f", "mpegts",
        "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate(timeout=10)
    if proc.returncode != 0:
        raise HTTPException(500, f"FFmpeg failed: {err.decode(errors='ignore')}")
    return Response(content=data, media_type="video/MP2T")

@app.get("/streams/{stream_key}/snapshot")
async def snapshot(stream_key: str):
    """
    Capture a single video frame from the RTSP stream and return it as JPEG.
    """
    rtsp = f"rtsp://localhost:8554/live/{stream_key}"
    # Build ffmpeg command to grab one frame and output to stdout
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp,
        "-frames:v", "1",
        "-f", "image2",
        "pipe:1"
    ]
    # Launch ffmpeg and capture stdout/stderr
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        data, err = proc.communicate(timeout=5)  # give ffmpeg up to 5 seconds
    except subprocess.TimeoutExpired:
        proc.kill()
        raise HTTPException(504, "Timeout capturing snapshot")
    if proc.returncode != 0:
        raise HTTPException(500, f"FFmpeg failed: {err.decode(errors='ignore')}")
    # Return the JPEG image
    return Response(content=data, media_type="image/jpeg")

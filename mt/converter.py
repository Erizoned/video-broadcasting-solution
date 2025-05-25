import re
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:3006"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Точка добавления путей в MediaMTX
MEDIA_MTX_API = "http://localhost:9997/v3/config/paths/add"
MEDIA_MTX_HOST = "localhost"
MEDIA_MTX_PORT = 9997
MEDIA_MTX_BASE = f"http://{MEDIA_MTX_HOST}:{MEDIA_MTX_PORT}/v3"
PATHS_CONFIG = f"{MEDIA_MTX_BASE}/config/paths"
PATHS_API    = f"{MEDIA_MTX_BASE}/paths"


class StreamRegistration(BaseModel):
    """Модель для регистрации RTMP→RTSP конвертации"""
    rtmp_source: str  # полный RTMP URL


class PublishRequest(BaseModel):
    """Модель для эмуляции RTMP-публикации видеофайла"""
    video_path: str
    stream_key: str = "drone"
    rtmp_url: str = "rtmp://localhost/live"


@app.post("/register-stream")
async def register_stream(req: StreamRegistration):
    """
    Регистрирует RTMP-источник в MediaMTX для конвертации в RTSP.
    Заменяет localhost на nginx-rtmp для Docker-среды.
    """
    # нормализуем и перенаправляем хост внутри Docker
    src = req.rtmp_source.strip()
    local_match = re.match(r"^rtmp://(localhost|127\.0\.0\.1)(:\d+)?(/live/[^/]+)$", src)
    if local_match:
        host, port, path = local_match.groups()
        port = port or ":1935"
        src = f"rtmp://nginx-rtmp{port}{path}"

    # извлекаем ключ потока из пути
    m = re.match(r"^rtmp://[^/]+/live/([^/]+)$", src)
    if not m:
        raise HTTPException(400, detail="rtmp_source должен быть вида rtmp://<host>/live/<stream_key>")
    key = m.group(1)

    # формируем имя и публичный RTSP URL
    path_name = f"live/{key}"
    rtsp_url = f"rtsp://localhost:8554/{path_name}"

    # регистрируем путь в MediaMTX
    payload = {"source": src, "sourceOnDemand": True}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{PATHS_CONFIG}/add/{path_name}", json=payload)
    if resp.status_code != 200:
        raise HTTPException(500, detail=f"Ошибка регистрации: {resp.status_code} {resp.text}")

    return {"rtmp_source": req.rtmp_source, "rtsp_url": rtsp_url, "status": "registered"}


@app.get("/streams/{stream_key}")
async def get_stream_info(stream_key: str):
    """
    Возвращает детальную статистику по одному RTSP-потоку.
    Рассчитывает uptime и считает протоколы читателей.
    """
    url = f"{PATHS_API}/get/live/{stream_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    if resp.status_code == 404:
        raise HTTPException(404, detail="Stream not found")
    if resp.status_code != 200:
        raise HTTPException(500, detail=f"MediaMTX error: {resp.status_code}")

    info = resp.json()

    # вычисляем uptime
    uptime = None
    ready_ts = info.get("readyTime")
    if ready_ts:
        iso = ready_ts.rstrip('Z') + '+00:00'
        try:
            started = datetime.datetime.fromisoformat(iso)
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
            uptime = (now - started).total_seconds()
        except ValueError:
            uptime = None

    # считаем читателей по протоколам
    readers = info.get("readers", [])
    proto_counts: dict[str, int] = {}
    for r in readers:
        proto = r.get("protocol", "unknown")
        proto_counts[proto] = proto_counts.get(proto, 0) + 1

    return {
        "stream_key": stream_key,
        "status": "running" if info.get("ready") else "stopped",
        "uptime_seconds": uptime,
        "bytes_received": info.get("bytesReceived"),
        "bytes_sent": info.get("bytesSent"),
        "source": info.get("source"),
        "tracks": info.get("tracks"),
        "readers_count": len(readers),
    }


@app.get("/streams")
async def list_streams():
    """
    Список всех RTSP-потоков с базовой статистикой и группировкой треков.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PATHS_API}/list")
    if resp.status_code != 200:
        raise HTTPException(500, detail="Ошибка получения списка стримов")

    data = resp.json().get("items", [])
    result = []
    for itm in data:
        name = itm.get("name", "")
        key = name.split('/', 1)[-1]
        # считаем читателей
        readers = itm.get("readers", [])
        proto_counts: dict[str, int] = {}
        for r in readers:
            p = r.get("protocol", "unknown")
            proto_counts[p] = proto_counts.get(p, 0) + 1
        # группируем типы треков
        raw_tracks = itm.get("tracks", [])
        track_counts: dict[str, int] = {}
        for t in raw_tracks:
            if isinstance(t, dict):
                ttype = t.get("type") or "unknown"
            elif isinstance(t, str):
                ttype = t.split(":", 1)[0] if ":" in t else "unknown"
            else:
                ttype = "unknown"
            track_counts[ttype] = track_counts.get(ttype, 0) + 1

        result.append({
            "stream_key": key,
            "status": "running" if itm.get("ready") else "stopped",
            "ready_time": itm.get("readyTime"),
            "bytes_received": itm.get("bytesReceived"),
            "bytes_sent": itm.get("bytesSent"),
            "source": itm.get("source"),
            "readers_count": len(readers),
            "protocol_counts": proto_counts,
            "tracks": raw_tracks,
            "track_counts": track_counts,
        })
    return {"streams": result}


@app.get("/health")
async def health():
    """
    Проверка доступности MediaMTX.
    """
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(f"{PATHS_API}/list")
        if resp.status_code == 200:
            return {"status": "ok"}
    except httpx.RequestError:
        pass
    raise HTTPException(503, detail="MediaMTX unavailable")


@app.get("/streams/{stream_key}/preview")
def preview(stream_key: str):
    """
    Возвращает первые 5 секунд RTSP-потока как MPEG-TS.
    """
    rtsp = f"rtsp://{MEDIA_MTX_HOST}:8554/live/{stream_key}"
    cmd = [
        "ffmpeg", "-rtsp_transport", "tcp",
        "-i", rtsp,
        "-t", "5",
        "-c", "copy",
        "-f", "mpegts",
        "pipe:1",
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(500, detail="ffmpeg не найден в PATH")
    return StreamingResponse(proc.stdout, media_type="video/mp2t")

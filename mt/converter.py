import re
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
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

class StreamRegistration(BaseModel):
    rtmp_source: str  # полный RTMP URL

@app.post("/register-stream")
async def register_stream(req: StreamRegistration):
    rtmp_source_input = req.rtmp_source.strip()

    # Заменяем localhost на nginx-rtmp внутри Docker
    local_pattern = re.compile(r'^(rtmp://)(localhost|127\.0\.0\.1)(:\d+)?(/live/[^/]+)$')
    m_local = local_pattern.match(rtmp_source_input)
    if m_local:
        prefix, _, port, path = m_local.groups()
        port = port or ":1935"
        rtmp_source = f"{prefix}nginx-rtmp{port}{path}"
    else:
        rtmp_source = rtmp_source_input

    m = re.match(r"^rtmp://[^/]+/live/([^/]+)$", rtmp_source)
    if not m:
        raise HTTPException(400, detail="rtmp_source должен быть вида rtmp://<host>/live/<stream_key>")
    stream_key = m.group(1)

    path_name = f"live/{stream_key}"
    rtsp_url = f"rtsp://localhost:8554/{path_name}"

    payload = {
        "source": rtmp_source,
        "sourceOnDemand": True
    }
    url = f"{MEDIA_MTX_API}/{path_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        print(
            "[ERROR] MediaMTX registration failed.",
            f"URL: {url}",
            f"Status: {resp.status_code}",
            f"Response: {resp.text}"
        )
        raise HTTPException(
            500,
            detail=f"Ошибка регистрации в MediaMTX: {resp.status_code} {resp.text}"
        )

    return {
        "rtmp_source": rtmp_source_input,
        "rtsp_url": rtsp_url,
        "status": "registered"
    }

@app.get("/streams/{stream_key}")
async def get_stream_info(stream_key: str):
    """
    Get detailed status and stats for a specific stream_key.
    """
    path_name = f"live/{stream_key}"
    url = f"http://localhost:9997/v3/paths/get/{path_name}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code == 404:
        raise HTTPException(404, detail=f"Stream '{stream_key}' not found")
    if resp.status_code != 200:
        print(f"[ERROR] MediaMTX GET failed. URL: {url}, Status: {resp.status_code}, Body: {resp.text}")
        raise HTTPException(500, detail=f"Error fetching stream info: {resp.status_code}")

    info = resp.json()

    # Расчет аптайма
    ready_time_str = info.get("readyTime")
    uptime = None
    if ready_time_str:
        ts = ready_time_str
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        try:
            ready_dt = datetime.datetime.fromisoformat(ts)
            uptime = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - ready_dt).total_seconds()
        except Exception:
            uptime = None

    # Сбор статистики читателей
    readers = info.get("readers", [])
    protocol_counts = {}
    for r in readers:
        proto = r.get("protocol") or "unknown"
        protocol_counts[proto] = protocol_counts.get(proto, 0) + 1

    return {
        "stream_key": stream_key,
        "status": "running" if info.get("ready") else "stopped",
        "ready_time": info.get("readyTime"),
        "uptime_seconds": uptime,
        "bytes_received": info.get("bytesReceived"),
        "bytes_sent": info.get("bytesSent"),
        "packets_received": info.get("packetsReceived"),
        "packets_sent": info.get("packetsSent"),
        "source": info.get("source"),
        "source_on_demand": info.get("sourceOnDemand"),
        "tracks": info.get("tracks"),
        "readers_count": len(readers),
        "readers": readers,
        "protocol_counts": protocol_counts,
    }

@app.get("/streams")
async def list_streams():
    """
    Return a list of all registered RTSP streams with detailed stats.
    """
    url = "http://localhost:9997/v3/paths/list"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        print(f"[ERROR] MediaMTX list failed. URL: {url}, Status: {resp.status_code}, Body: {resp.text}")
        raise HTTPException(500, detail="Ошибка получения списка стримов")

    data = resp.json()
    items = data.get("items", [])
    streams = []
    for item in items:
        name = item.get("name", "")
        stream_key = name.split("/", 1)[1] if "/" in name else name

        # Сбор статистики читателей
        readers = item.get("readers", [])
        protocol_counts = {}
        for r in readers:
            proto = r.get("protocol") or "unknown"
            protocol_counts[proto] = protocol_counts.get(proto, 0) + 1

        # Группировка треков по типам (поддерживаем и dict, и str форматы)
        raw_tracks = item.get("tracks", [])
        track_types = {}
        for t in raw_tracks:
            if isinstance(t, dict):
                ttype = t.get("type") or "unknown"
            elif isinstance(t, str):
                ttype = t.split(":", 1)[0] if ":" in t else "unknown"
            else:
                ttype = "unknown"
            track_types[ttype] = track_types.get(ttype, 0) + 1

        streams.append({
            "stream_key": stream_key,
            "status": "running" if item.get("ready") else "stopped",
            "ready_time": item.get("readyTime"),
            "bytes_received": item.get("bytesReceived"),
            "bytes_sent": item.get("bytesSent"),
            "source": item.get("source"),
            "readers_count": len(readers),
            "protocol_counts": protocol_counts,
            "tracks": raw_tracks,
            "track_counts_by_type": track_types,
        })

    return {"streams": streams}

@app.get("/health")
async def health():
    """
    Проверяет доступность MediaMTX.
    """
    url = "http://localhost:9997/v3/paths/list"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            return {"status": "ok"}
        raise HTTPException(503, detail=f"MediaMTX unhealthy: {resp.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(503, detail=f"Cannot reach MediaMTX: {e}")

@app.get("/streams/{stream_key}/preview")
def preview(stream_key: str):
    """
    Возвращает первые 5 секунд RTSP-потока как MPEG-TS.
    """
    rtsp_url = f"rtsp://localhost:8554/live/{stream_key}"
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-t", "5",
        "-c", "copy",
        "-f", "mpegts",
        "pipe:1"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg не найден в PATH")
    return StreamingResponse(proc.stdout, media_type="video/mp2t")

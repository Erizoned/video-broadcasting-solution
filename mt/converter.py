import re 
import httpx  
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel 
import subprocess  
import datetime 
from fastapi.middleware.cors import CORSMiddleware 
import logging  
import os  

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s', 
    handlers=[
        logging.FileHandler('converter.log', encoding='utf-8'), 
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)  # логгер для текущего модуля

app = FastAPI()

# Настройка CORS (разрешение запросов с любых источников)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Константы для работы с MediaMTX
MEDIA_MTX_HOST = "localhost"
MEDIA_MTX_PORT = 9997
MEDIA_MTX_BASE = f"http://{MEDIA_MTX_HOST}:{MEDIA_MTX_PORT}/v3"
PATHS_CONFIG = f"{MEDIA_MTX_BASE}/config/paths"  # для управления путями
PATHS_API    = f"{MEDIA_MTX_BASE}/paths"        # для получения информации о путях

# Модель данных для регистрации конвертации потока
class StreamRegistration(BaseModel):
    """Модель для регистрации RTMP→RTSP конвертации"""
    rtmp_source: str

# Middleware для логирования всех HTTP-запросов и ответов
@app.middleware('http')
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}") 
    try:
        response = await call_next(request) 
        logger.info(f"← {response.status_code} {request.url.path}") 
        return response
    except Exception as e:
        logger.error(f"‼ Exception on {request.method} {request.url.path}: {e}")
        raise

# Эндпоинт: конвертация RTMP потока в RTSP
@app.post("/stream/convert")
async def register_stream(req: StreamRegistration):
    logger.info(f"Start converting stream: {req.rtmp_source}")
    # нормализуется и перенаправляется хост внутри Docker, если это локальный RTMP
    src = req.rtmp_source.strip()
    local_match = re.match(r"^rtmp://(localhost|127\.0\.0\.1)(:\d+)?(/live/[^/]+)$", src)
    if local_match:
        host, port, path = local_match.groups()
        port = port or ":1935"
        # заменяется на сетевое имя контейнера nginx-rtmp
        src = f"rtmp://nginx-rtmp{port}{path}"
        logger.info(f"Redirected src to Docker network: {src}")

    # извлекается ключ потока из URL (последняя часть после /live/)
    m = re.match(r"^rtmp://[^/]+/live/([^/]+)$", src)
    if not m:
        logger.error("Bad rtmp_source format")
        raise HTTPException(400, detail="rtmp_source должен быть вида rtmp://<host>/live/<stream_key>")
    key = m.group(1)

    # формируется имя пути и итоговый RTSP URL
    path_name = f"live/{key}"
    rtsp_url = f"rtsp://{MEDIA_MTX_HOST}:8554/{path_name}"
    logger.info(f"Register path {path_name} → {rtsp_url}")

    # регистрируется путь в MediaMTX через HTTP API
    payload = {"source": src, "sourceOnDemand": True}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{PATHS_CONFIG}/add/{path_name}", json=payload)
    if resp.status_code != 200:
        logger.error(f"MediaMTX register error {resp.status_code}: {resp.text}")
        raise HTTPException(500, detail=f"Ошибка регистрации: {resp.status_code} {resp.text}")

    logger.info(f"Stream registered: {key}")
    # возвращение исходного RTMP и новый RTSP URL
    return {"rtmp_source": req.rtmp_source, "rtsp_url": rtsp_url, "status": "registered"}

# Эндпоинт: получение информации о конкретном потоке
@app.get("/streams/{stream_key}")
async def get_stream_info(stream_key: str):
    logger.info(f"Fetch info for stream: {stream_key}")
    url = f"{PATHS_API}/get/live/{stream_key}"  # URL для получения статуса
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    if resp.status_code == 404:
        logger.warning(f"Stream not found: {stream_key}")
        raise HTTPException(404, detail="Stream not found")
    if resp.status_code != 200:
        logger.error(f"MediaMTX GET error {resp.status_code}")
        raise HTTPException(500, detail=f"MediaMTX error: {resp.status_code}")

    info = resp.json()  # реакция API MediaMTX
    # вычисление времени работы (uptime) в секундах
    uptime = None
    ready_ts = info.get("readyTime")
    if ready_ts:
        iso = ready_ts.rstrip('Z') + '+00:00'
        try:
            started = datetime.datetime.fromisoformat(iso)
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
            uptime = (now - started).total_seconds()
        except ValueError:
            logger.warning("Failed parse readyTime for uptime")

    # считается количество читателей по протоколам
    readers = info.get("readers", [])
    proto_counts = {}
    for r in readers:
        p = r.get("protocol", "unknown")
        proto_counts[p] = proto_counts.get(p, 0) + 1

    # формируется ответ для клиента
    result = {
        "stream_key": stream_key,
        "status": "running" if info.get("ready") else "stopped",
        "uptime_seconds": uptime,
        "bytes_received": info.get("bytesReceived"),
        "bytes_sent": info.get("bytesSent"),
        "source": info.get("source"),
        "tracks": info.get("tracks"),
        "readers_count": len(readers),
        "protocol_counts": proto_counts,
    }
    logger.info(f"Info returned for {stream_key}: {result}")
    return result

# Эндпоинт: список всех зарегистрированных потоков
@app.get("/streams")
async def list_streams():
    logger.info("List all streams")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PATHS_API}/list")
    if resp.status_code != 200:
        logger.error(f"MediaMTX list error {resp.status_code}")
        raise HTTPException(500, detail="Ошибка получения списка стримов")

    items = resp.json().get("items", [])
    result = []
    for itm in items:
        key = itm.get("name", "").split('/', 1)[-1]
        readers = itm.get("readers", [])
        proto_counts = {}
        for r in readers:
            p = r.get("protocol", "unknown")
            proto_counts[p] = proto_counts.get(p, 0) + 1

        raw_tracks = itm.get("tracks", [])
        track_counts = {}
        for t in raw_tracks:
            if isinstance(t, dict):
                ttype = t.get("type") or "unknown"
            elif isinstance(t, str):
                ttype = t.split(":", 1)[0]
            else:
                ttype = "unknown"
            track_counts[ttype] = track_counts.get(ttype, 0) + 1

        entry = {
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
        }
        result.append(entry)

    logger.info(f"Streams list returned ({len(result)} items)")
    return {"streams": result}

# Эндпоинт: проверка доступности MediaMTX
@app.get("/health")
async def health():
    logger.info("Health check")
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(f"{PATHS_API}/list")
        if resp.status_code == 200:
            logger.info("MediaMTX is healthy")
            return {"status": "ok"}
    except httpx.RequestError as e:
        logger.error(f"Health check failed: {e}")
    raise HTTPException(503, detail="MediaMTX unavailable")

# Эндпоинт: получение короткого превью потока (первые 5 секунд)
@app.get("/streams/{stream_key}/preview")
def preview(stream_key: str):
    logger.info(f"Preview request for: {stream_key}")
    rtsp = f"rtsp://{MEDIA_MTX_HOST}:8554/live/{stream_key}"
    # команда ffmpeg для захвата 5 секунд и копирования потока без перекодирования
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
        logger.error("ffmpeg not found")
        raise HTTPException(500, detail="ffmpeg не найден в PATH")
    return StreamingResponse(proc.stdout, media_type="video/mp2t")

# Эндпоинт: получение последних строк из лога приложения
@app.get("/logs")
async def get_logs(lines: int = Query(200, ge=1, le=1000)):
    logger.info(f"Fetching last {lines} log lines")
    log_path = os.path.join(os.path.dirname(__file__), 'converter.log')
    if not os.path.isfile(log_path):
        logger.warning("Log file not found")
        return {"logs": []}
    # читается файл лога и отдаются последние N строк
    with open(log_path, encoding='utf-8') as f:
        all_lines = f.readlines()
    recent = all_lines[-lines:]
    return {"logs": recent}

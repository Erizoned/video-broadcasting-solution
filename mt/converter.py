import re
import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import subprocess
import tempfile
import os
from fastapi.responses import StreamingResponse

app = FastAPI()

# Точка добавления путей в MediaMTX
MEDIA_MTX_API = "http://localhost:9997/v3/config/paths/add"

class StreamRegistration(BaseModel):
    rtmp_source: str  # теперь передаем полный RTMP URL

@app.post("/register-stream")
async def register_stream(req: StreamRegistration):
    # 1. Получаем исходный RTMP URL от пользователя
    rtmp_source_input = req.rtmp_source.strip()

    # 2. Если пользователь передал localhost или 127.0.0.1, 
    #    заменяем их на имя контейнера nginx-rtmp, чтобы внутри Docker-сети MediaMTX мог достучаться
    #    (не говнокод, а настройка сетевого окружения Docker)
    local_pattern = re.compile(r'^(rtmp://)(localhost|127\.0\.0\.1)(:\d+)?(/live/[^/]+)$')
    m_local = local_pattern.match(rtmp_source_input)
    if m_local:
        prefix, _, port, path = m_local.groups()
        port = port or ":1935"  # если порт не указан, по умолчанию 1935
        rtmp_source = f"{prefix}nginx-rtmp{port}{path}"
    else:
        # для всех остальных источников оставляем URL без изменений
        rtmp_source = rtmp_source_input

    # 3. Проверяем итоговый RTMP URL и извлекаем stream_key
    m = re.match(r"^rtmp://[^/]+/live/([^/]+)$", rtmp_source)
    if not m:
        raise HTTPException(400, detail="rtmp_source должен быть вида rtmp://<host>/live/<stream_key>")
    stream_key = m.group(1)

    # 4. Формируем путь (live/<stream_key>) и итоговый RTSP URL для клиента
    path_name = f"live/{stream_key}"
    rtsp_url = f"rtsp://localhost:8554/{path_name}"

    # 5. Готовим тело запроса к MediaMTX
    payload = {
        "source": rtmp_source,           # используем уже скорректированный URL
        "sourceOnDemand": True
    }

    # 6. Отправляем запрос на регистрацию пути в MediaMTX
    url = f"{MEDIA_MTX_API}/{path_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)

    # 7. Обрабатываем возможную ошибку от MediaMTX
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

    # 8. Успешный ответ — возвращаем клиенту вводимый RTMP и сформированный RTSP URL
    return {
        "rtmp_source": rtmp_source_input,  # показываем исходный URL, как его ввёл пользователь
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
def preview(stream_key: str):
    """
    Возвращает первые 5 секунд RTSP-потока как MPEG-TS.
    """
    rtsp_url = f"rtsp://localhost:8554/live/{stream_key}"
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-t", "5",           # длительность клипа
        "-c", "copy",        # не перекодируем
        "-f", "mpegts",      # контейнер MPEG-TS
        "pipe:1"             # выводим в stdout
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg не найден в PATH")

    # StreamingResponse автоматически завершится, когда FFmpeg закончит писать
    return StreamingResponse(
        proc.stdout,
        media_type="video/mp2t"
    )
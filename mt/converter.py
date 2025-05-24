import re
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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


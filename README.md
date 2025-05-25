## 1 Поднять Python Сервис для симуляции RTMP потока из указанного MP4 Файла

(На пути /backend)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

## 2 Поднять Python Сервис для конвертации RTMP потока в RTSP (Основной API)

(На пути /mt)
uvicorn converter:app --reload --host 0.0.0.0 --port 8001

## 3 Инициализация всех основных сервисов через Docker compose:

(На пути /mt)
docker compose down
docker compose up -d

# Как проверить / Начать стрим:

### 1. Сделать инициализацию RTMP потока:

POST http://localhost:8000/stream/start
Пример Request Body:
```json
{
  "video_path": "(путь до файла)",
  "stream_key": "sample1",
  "rtmp_url": "rtmp://localhost:1935/live"
}
```
Пример пути до файла: "C:\\Users\\rshal\\.hackathon\\video-broadcasting-solution\\sample1.mp4"
stream_key: ключ, обозначающий стрим
### 2. Конвертация RTMP потока на RTSP:

POST http://localhost:8001/register-stream
Пример Request Body:

```json
{
  "rtmp_source": "rtmp://localhost:1935/live/sample1"
}
```

Выдаваемая RTSP ссылка (rtsp_url) работает не сразу, после вставки ссылки в VLC нужно подождать примерно 20 секунд и поток запустится
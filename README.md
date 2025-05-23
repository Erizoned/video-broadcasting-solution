### Как запустить backend:

## 1

PS C:\Users\rshal.hackathon\video-broadcasting-solution\backend> uvicorn main:app --reload --host 0.0.0.0 --port 8000,

Запуск FastAPI (Сервис для генерации стрима)


## 2

PS C:\Users\rshal.hackathon\video-broadcasting-solution\new_conenter> docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp,

Поднятие RTMP сервера  - заранее написать нужно: docker rm -f nginx-rtmp;


## 3

POST http://localhost:8000/stream/start

{
  "video_path": "C:\\Users\\rshal\\.hackathon\\video-broadcasting-solution\\sample1.mp4",
  "stream_key": "drone",
  "rtmp_url": "rtmp://localhost:1935/live"
}

## 4

PS C:\Users\rshal.hackathon\video-broadcasting-solution\backend> .\stream.bat "C:\Users\rshal.hackathon\video-broadcasting-solution\sample1.mp4" drone,

Вторая часть стриминг сервиса


## 5

PS C:\Users\rshal.hackathon\video-broadcasting-solution\mt> docker compose up -d,

поднятие mediaMTX
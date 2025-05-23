### Как запустить backend:

## 1
На пути \backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

## 2

POST http://localhost:8000/stream/start

{
  "video_path": "C:\\Users\\rshal\\.hackathon\\video-broadcasting-solution\\sample1.mp4",
  "stream_key": "drone",
  "rtmp_url": "rtmp://localhost:1935/live"
}

## 3

На пути \backend: (Одной командой)

docker rm -f nginx-rtmp; docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp

## 4

На пути \backend
.\stream.bat "C:\Users\rshal.hackathon\video-broadcasting-solution\sample1.mp4" drone


## 5

На пути \mt
docker compose up -d,
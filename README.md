## 1 
В любой директории
docker rm -f nginx-rtmp
docker run -d --name nginx-rtmp -p 1935:1935 -p 80:80 tiangolo/nginx-rtmp

## 2
В директории /backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

## 3
В директории /backend
.\stream.bat "C:\Users\{user}\Videos\sample1.mp4" sample1


## 4
В директории /mt
docker compose down
docker compose up -d
uvicorn converter:app --reload --host 0.0.0.0 --port 8001

## 5
POST http://localhost:8000/stream/start (если в этом есть надобность)

{
  "video_path": "C:\\Users\\rshal\\.hackathon\\video-broadcasting-solution\\sample1.mp4",
  "stream_key": "drone",
  "rtmp_url": "rtmp://localhost:1935/live"
}

## 6
POST http://localhost:8001/register/stream
{
  "rtmp_source": "ссылка на rtmp"
}
**Как запустить:**
1. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустить FastAPI-сервер:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Для демонстрации потока используйте VLC или ffplay:
   ```bash
   ffplay rtsp://localhost:8554/<stream_name>
   ```  

Теперь два endpoint’а:
- `POST /convert` — начать конвертацию RTMP → RTSP
- `DELETE /convert/{stream_name}` — остановить конвертацию
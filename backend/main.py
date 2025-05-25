from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import os
import time
from typing import Dict

app = FastAPI()

# Хранилище запущенных процессов ffmpeg и batch
processes: Dict[str, subprocess.Popen] = {}

class PublishRequest(BaseModel):
    video_path: str               # Локальный путь к видеофайлу
    stream_key: str = "drone"   # Ключ потока (часть URL)
    rtmp_url: str = "rtmp://localhost/live"  # Базовый RTMP-адрес

@app.post("/stream/start")
async def start_stream(req: PublishRequest):
    """
    Запускает два процесса:
    1) FFmpeg читает видео и публикует его в RTMP-сервер (loop).
    2) stream.bat выполняет аналогичную публикацию (для совместимости).
    """
    key = req.stream_key
    video = req.video_path
    target = f"{req.rtmp_url.rstrip('/')}/{key}"

    # 1. Проверка дублирования
    if key in processes and processes[key].poll() is None:
        raise HTTPException(409, f"Stream '{key}' уже запущен")

    # 2. Проверка существования файла
    if not os.path.isfile(video):
        raise HTTPException(400, f"Видео не найдено: {video}")

    # 3. Запуск FFmpeg для бесконечного loop
    ffmpeg_cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1",
        "-i", video, "-c", "copy", "-f", "flv", target
    ]
    try:
        proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HTTPException(500, "ffmpeg не найден в PATH")
    except Exception as e:
        raise HTTPException(500, f"Ошибка запуска ffmpeg: {e}")

    # Небольшая задержка и проверка, что процесс не завершился сразу
    time.sleep(0.5)
    if proc.poll() is not None:
        err = proc.stderr.read().decode(errors='ignore').strip()
        raise HTTPException(500, f"ffmpeg завершился сразу: {err or 'без вывода'}")

    processes[key] = proc

    # 4. Запуск дополнительного скрипта stream.bat 
    script_dir = os.path.dirname(__file__)
    batch_path = os.path.join(script_dir, "stream.bat")
    if not os.path.isfile(batch_path):
        proc.terminate()
        raise HTTPException(500, f"stream.bat не найден: {batch_path}")

    bat_cmd = ["cmd", "/c", batch_path, video, key]
    try:
        bat_proc = subprocess.Popen(
            bat_cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        proc.terminate()
        raise HTTPException(500, f"Не удалось запустить stream.bat: {e}")

    processes[f"{key}_bat"] = bat_proc

    # 5. Сбор логов для отладки
    time.sleep(2)
    out = bat_proc.stdout.read() or b""
    err = bat_proc.stderr.read() or b""
    logs = (out + err).decode(errors='ignore').splitlines()[-5:]

    return {
        "message": f"Stream '{key}' запущен на {target}",
        "batch_logs": logs
    }

# Остановка RTMP стрима 
@app.delete("/stream/stop")
async def stop_stream(stream_key: str = Query(..., description="Stream key")):
    """
    Останавливает связанные с stream_key процессы:
    - основный ffmpeg
    - вспомогательный batch
    """
    # Остановка ffmpeg
    proc = processes.get(stream_key)
    if not proc or proc.poll() is not None:
        raise HTTPException(404, f"Stream '{stream_key}' не запущен")
    proc.terminate()
    proc.wait(timeout=5)
    processes.pop(stream_key, None)

    # Остановка batch
    bat_key = f"{stream_key}_bat"
    bat_proc = processes.get(bat_key)
    if bat_proc and bat_proc.poll() is None:
        bat_proc.terminate()
        bat_proc.wait(timeout=5)
        processes.pop(bat_key, None)

    return {"message": f"Stream '{stream_key}' остановлен"}


#Статус стрима
@app.get("/stream/status")
async def stream_status(stream_key: str = Query(..., description="Stream key")):
    """
    Возвращает статус: 'running' если процесс жив, иначе 'stopped'.
    """
    proc = processes.get(stream_key)
    return {
        "stream_key": stream_key,
        "status": "running" if proc and proc.poll() is None else "stopped"
    }

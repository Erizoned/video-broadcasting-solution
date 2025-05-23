# Используем лёгкий образ Python
FROM python:3.10-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY main.py ./

# Открываем порт FastAPI
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
@echo off
REM Отключаем вывод команд в консоль для чистоты логов
set VIDEO=%\~1
REM Первый аргумент: путь к видеофайлу
set KEY=%\~2
REM Второй аргумент: ключ потока (имя канала)

if "%VIDEO%"=="" (
REM Если видео не передано — выводим подсказку по использованию
echo Usage: stream.bat path\to\video.mp4 \[stream\_key]
exit /b 1
)

if "%KEY%"=="" set KEY=drone
REM Если ключ не передан — используем значение по умолчанию 'drone'

echo Starting stream for video: %VIDEO% with key: %KEY%
REM Логируем начало работы с указанием входного файла и ключа

echo FPS set to 15
REM Информируем, что частота кадров установлена в 15

REM Запускаем ffmpeg:
REM -re               : воспроизводим вход как в реальном времени
REM -stream\_loop -1   : зацикливаем видео бесконечно
REM -i "%VIDEO%"     : входной файл
REM -vf "fps=15"     : фильтр изменения FPS на 15
REM -c\:v libx264      : кодек видео H.264 (libx264)
REM -preset veryfast: предварительные настройки скорости/качества
REM -tune zerolatency : минимальная задержка кодирования
REM -c\:a aac          : кодек аудио AAC
REM -ar 44100         : частота аудио 44.1 кГц
REM -b\:a 128k         : битрейт аудио 128 кбит/с
REM -f flv            : выходной формат FLV (для RTMP)
REM "rtmp\://127.0.0.1/live/%KEY%": адрес RTMP-сервера и ключ потока
ffmpeg -re -stream\_loop -1 -i "%VIDEO%" ^
-vf "fps=15" ^
-c\:v libx264 -preset veryfast -tune zerolatency ^
-c\:a aac -ar 44100 -b\:a 128k ^
-f flv "rtmp\://127.0.0.1/live/%KEY%"

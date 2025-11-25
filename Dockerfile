# Используем официальный легкий образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Обновляем пакеты и устанавливаем системные зависимости для Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем только файл с зависимостями
# Это позволяет Docker кэшировать этот шаг
COPY requirements.txt .

# Устанавливаем все зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь остальной код проекта в рабочую директорию
COPY . .

# Указываем команду для запуска бота при старте контейнера
CMD ["python", "main.py"]
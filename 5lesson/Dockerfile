FROM python:3.11-slim

# Устанавливаем зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY req.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r req.txt

# Копируем весь проект
COPY . .

# Создаём .env файл внутри контейнера
RUN echo "DB_HOST=quotes-db" > .env && \
    echo "DB_PORT=5432" >> .env && \
    echo "DB_NAME=postgres" >> .env && \
    echo "DB_USER=postgres" >> .env && \
    echo "DB_PASSWORD=Fe2006dor" >> .env && \
    echo "APP_HOST=0.0.0.0" >> .env && \
    echo "APP_PORT=8001" >> .env

# Открываем порт
EXPOSE 8001

# Запускаем приложение
CMD ["python", "main.py"]
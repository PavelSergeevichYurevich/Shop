FROM python:3.12-slim

# Важно: рабочая директория — КОРЕНЬ проекта
WORKDIR /app_root

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Указываем Python искать модули прямо в корне контейнера
ENV PYTHONPATH=/app_root

# 1. Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Копируем ВСЁ дерево проекта (alembic.ini, папки app и migrations)
COPY alembic.ini .
COPY ./migrations ./migrations
COPY ./app ./app

# 3. Даем права на скрипт (он теперь по пути /app_root/app/entrypoint.sh)
RUN chmod +x ./app/entrypoint.sh

EXPOSE 8000

# Запускаем через ENTRYPOINT
ENTRYPOINT ["./app/entrypoint.sh"]

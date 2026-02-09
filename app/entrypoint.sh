#!/bin/sh
set -e

echo "Контекст запуска: $(pwd)"

echo "Запуск миграций..."
# Alembic увидит alembic.ini в текущей папке и пойдет в ./migrations
alembic upgrade head

echo "Запуск сервера..."
# Запуск через модуль app.main, чтобы работали импорты from app.routes...
if [ "$DEBUG" = "true" ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi

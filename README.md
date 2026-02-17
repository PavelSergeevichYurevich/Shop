# Shop Backend (FastAPI)

API интернет-магазина с авторизацией, RBAC, управлением остатками и миграциями.

## Что реализовано

- FastAPI + SQLAlchemy 2.0 + Pydantic v2.
- JWT access/refresh токены.
- Refresh flow и logout/revoke refresh-токенов.
- RBAC: роли `user` / `admin` на ключевых эндпоинтах.
- Заказы с фиксацией цены на момент покупки (`price_at_purchase`).
- Корректное списание/возврат товара на склад.
- Единый формат ошибок через глобальные handlers.
- Alembic миграции.
- Docker Compose (app + Postgres).
- CI в GitHub Actions.
- Тесты `pytest` (все зеленые).

## Стек

- Python 3.12+ (локально у тебя может быть 3.13, это ок)
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite (для тестов in-memory)
- Alembic
- Pytest
- Docker / Docker Compose

## Структура

- `app/routes/` — роутеры (`auth`, `customer`, `item`, `order`)
- `app/models/` — SQLAlchemy модели
- `app/schemas/` — Pydantic схемы
- `app/core/` — настройки и обработчики ошибок
- `migrations/` — Alembic
- `tests/` — тесты
- `.github/workflows/ci.yml` — CI

## Конфигурация

Приложение читает настройки из `.env` (см. `app/core/settings.py`).

Ключевые переменные:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `APP_HOST`
- `APP_PORT`
- `APP_ENV`
- `DEBUG`

Для Docker используется `.env.docker`.

## Локальный запуск

1. Установить зависимости:

```bash
python -m pip install -r requirements.txt
```

2. Настроить `.env` (особенно `DATABASE_URL` и `SECRET_KEY`).

3. Применить миграции:

```bash
alembic upgrade head
```

4. Запустить API:

```bash
uvicorn app.main:app --reload
```

## Запуск через Docker

```bash
docker compose up --build
```

Что происходит:

- поднимается `shop_db` (Postgres),
- поднимается `shop_app`,
- в `entrypoint` автоматически выполняется `alembic upgrade head`,
- стартует `uvicorn`.

Остановка:

```bash
docker compose down
```

## Документация API

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

## Тесты

Запуск всех тестов:

```bash
./env/bin/pytest -q
```

Запуск только `order` тестов:

```bash
./env/bin/pytest -q tests/test_order.py
```

## CI

Workflow: `.github/workflows/ci.yml`

На `push` и `pull_request` в `main/master` запускается:

- установка зависимостей,
- `pytest --cov=app --cov-report=term-missing`.

## Текущее состояние проекта

- Основной функционал и безопасность для портфолио закрыты.
- Полный набор тестов проходит.
- Проект готов к демонстрации как backend pet-project уровня `junior / junior+`.

# Booking Service

Сервис для записи на встречи. Тестовое задание Python Backend Developer.

## Стек

- **FastAPI** — веб-фреймворк (асинхронный режим, async/await)
- **SQLAlchemy 2.0** + **asyncpg** — асинхронная работа с PostgreSQL
- **Alembic** — миграции базы данных
- **Celery** + **Redis** — фоновая обработка задач
- **Pydantic** — валидация данных и сериализация
- **SlowAPI** — rate limiting
- **Docker** + **docker-compose** — контейнеризация
- **pytest** — тестирование (83% покрытие)

---

## Быстрый старт (Docker)

### 1. Клонировать репозиторий

```bash
git clone git@github.com:tamoykinden/BookingService.git
cd booking_service
```

### 2. Создать .env из шаблона

```bash
cp .env.example .env
```

### 3. Запустить все сервисы

```bash
docker-compose up --build
```

Поднимутся:
- **API** — http://localhost:8000
- **Swagger UI** — http://localhost:8000/docs
- **PostgreSQL** — порт 5432
- **Redis** — порт 6379
- **Celery worker** — обрабатывает задачи

### 4. Применить миграции (если не применились автоматически)

```bash
docker-compose exec web alembic upgrade head
```

### 5. Остановить

```bash
docker-compose down
```

---

## Локальный запуск (без Docker)

### Требования

- Python 3.12+
- PostgreSQL 15+
- Redis 7+

### 1. Клонировать и перейти в папку

```bash
git clone git@github.com:tamoykinden/BookingService.git
cd booking_service
```

### 2. Виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить .env

```bash
cp .env.example .env
```

Отредактировать `.env` для локального подключения:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=user
DB_PASS=password
DB_NAME=booking_db

REDIS_HOST=localhost
REDIS_PORT=6379
```

### 5. Создать базу данных

```bash
psql -U postgres
```

```sql
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE booking_db OWNER "user";
GRANT ALL PRIVILEGES ON DATABASE booking_db TO "user";
\q
```

### 6. Применить миграции

```bash
alembic upgrade head
```

### 7. Запустить Redis

```bash
redis-server
```

### 8. Запустить API (терминал 1)

```bash
uvicorn app.main:app --reload --port 8000
```

### 9. Запустить Celery воркер (терминал 2)

```bash
celery -A app.celery_app worker --loglevel=info
```

### 10. Проверить

- API: http://localhost:8000/bookings/
- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API

### Эндпоинты

**POST /bookings/** — создать бронирование  
**GET /bookings/{id}** — получить бронирование по ID  
**GET /bookings/** — список броней с фильтрацией и пагинацией  
**DELETE /bookings/{id}** — отменить бронирование (только pending)  

### Параметры GET /bookings/

- `status` — фильтр по статусу (pending, confirmed, failed, cancelled)
- `page` — номер страницы (по умолчанию 1)
- `size` — размер страницы (по умолчанию 10, максимум 100)

### Тело POST /bookings/

```json
{
  "name": "Иван Петров",
  "meeting_time": "2026-06-20T15:00:00",
  "service_type": "Консультация"
}
```

### Статусы бронирования

- `pending` — создана, ожидает обработки воркером
- `confirmed` — успешно обработана (85% вероятность)
- `failed` — ошибка обработки (15% вероятность)
- `cancelled` — отменена пользователем

### Rate limiting

POST /bookings/ — не более 5 запросов в минуту. При превышении возвращается 429.


## Фоновая обработка (Celery)

### Как работает

1. Пользователь создаёт бронь → статус `pending`
2. Воркер получает задачу мгновенно
3. Имитация вызова внешнего сервиса:
   - **85%** — успех, статус `confirmed`, лог "уведомление отправлено клиенту"
   - **15%** — ошибка, статус `failed`
4. При ошибке — **retry** до 3 раз с экспоненциальным backoff

### Идемпотентность

Задача проверяет статус перед обработкой:
- Если статус не `pending` — завершается без изменений
- Повторный запуск с тем же `booking_id` безопасен

Это гарантирует, что бронь не будет обработана дважды при ретреях или сбоях.


## Тесты

```bash
# Все тесты
pytest -v

# С покрытием
pytest --cov=app --cov-report=term-missing -v
```

### Что тестируется

- **API эндпоинты**: создание, получение, список, отмена, валидация
- **Воркер**: успешная обработка, идемпотентность
- **Граничные случаи**: 404, 422, 400


## Makefile

```bash
make dev      # Запуск API
make worker   # Запуск Celery воркера
make test     # Запуск тестов
```


## Технические решения

### Почему FastAPI

- Высокая производительность на async/await
- Автоматическая документация (Swagger)
- Встроенная валидация через Pydantic
- Dependency для чистого кода

### Асинхронная БД + синхронный воркер

- **API** работает на `AsyncSession` с драйвером `asyncpg` — обрабатывает много запросов одновременно
- **Celery воркер** использует синхронную сессию (`psycopg2`) — Celery не дружит с `asyncio.run()`, поэтому воркер синхронный
- Оба подключения работают с одной БД, не мешая друг другу

### Разделение моделей и схем

- **SQLAlchemy модели** (`models/`) — структура таблиц в БД
- **Pydantic схемы** (`schemas/`) — валидация входных данных и формат ответов API
- Разные классы для создания (`BookingCreate`) и ответа (`BookingResponse`)

Это стандарт FastAPI по принципу Separation of Concerns — БД и API не должны быть связаны напрямую.

### Идемпотентность воркера

Задача `process_booking` перед обработкой проверяет статус брони. Если он не `pending` — задача завершается без изменений. Это гарантирует:
- Безопасность при ретреях Celery
- Отсутствие дублей при случайном повторном запуске
- Сохранение конечного статуса (не перезаписывается)

### Дополнительные плюсы (сверх требований)

- Retry с экспоненциальным backoff для упавших задач
- Structured logging в формате JSON в Celery-воркере
- Rate limiting на POST /bookings (SlowAPI)
- Makefile для удобства разработки
- Покрытие тестами 83%
- `.env.example` для быстрой настройки
```
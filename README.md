# Курсовая работа — Архитектура приложений (оценка 3)

Клиент-серверное приложение из двух сервисов на Python/FastAPI:

- **user-service** — CRUD пользователей (PostgreSQL), cache-aside кеширование (KeyDB/Redis), публикация события `user.created` в RabbitMQ.
- **notification-service** — подписчик на события RabbitMQ, обрабатывает уведомления о новых пользователях.

Покрывает требования трёх лабораторных:
1. Контейнеризация (Docker, docker-compose)
2. Кеширование (KeyDB, cache-aside)
3. Event-driven архитектура (RabbitMQ, topic exchange)

## Структура репозитория

```
.
├── docker-compose.yml
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py        — FastAPI роуты (CRUD)
│       ├── database.py    — подключение к Postgres
│       ├── models.py      — ORM-модель User
│       ├── schemas.py     — Pydantic-схемы
│       ├── cache.py       — cache-aside логика (KeyDB)
│       ├── events.py      — публикация событий в RabbitMQ
│       └── crud.py        — бизнес-логика
└── notification-service/
    ├── Dockerfile
    ├── requirements.txt
    └── app/main.py        — консьюмер RabbitMQ
```

## Запуск

```bash
docker compose up -d --build
```

После запуска:
- API доступен на `http://localhost:8080` (Swagger UI: `http://localhost:8080/docs`)
- RabbitMQ Management UI: `http://localhost:15672` (guest/guest)
- PostgreSQL: `localhost:5432` (postgres/postgres, база `courseapp`)
- KeyDB: `localhost:6379`

Логи второго сервиса (видно обработку событий):
```bash
docker logs -f notification-service
```

## Проверка работы

1. Создать пользователя:
   ```bash
   curl -X POST http://localhost:8080/users -H "Content-Type: application/json" \
        -d '{"name": "Ivan Ivanov", "email": "ivan@example.com"}'
   ```
   В логах `notification-service` появится строка `Notification: user created -> {...}`.

2. Запросить пользователя дважды по id — в логах `user-service` будет видно `Cache miss` при первом запросе и `Cache hit` при втором:
   ```bash
   docker logs -f user-service
   ```

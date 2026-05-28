# Habit Tracker

Полнофункциональный трекер привычек с веб-интерфейсом, API, геймификацией и push-уведомлениями.

## Описание

Habit Tracker помогает пользователю формировать регулярные привычки: создавать задачи, отмечать выполнение, получать очки и уровни, а также включать push-напоминания.

Проект разделен на:
- `backend` на FastAPI (REST API, авторизация, работа с БД, планировщик уведомлений);
- `frontend` на Streamlit (UI для регистрации, логина, управления привычками и включения push).

## Возможности

- Регистрация и вход по email/паролю.
- JWT-аутентификация и защищенные эндпоинты.
- Создание привычек с описанием, временем напоминания и днями недели.
- Просмотр списка своих привычек.
- Отметка выполнения привычки за текущий день.
- Геймификация: начисление очков и повышение уровня.
- Push-подписка и отписка через Web Push.
- Фоновый scheduler, который отправляет напоминания.

## Стек

### Backend
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL (`psycopg2-binary`, `asyncpg` в зависимостях)
- Pydantic
- python-jose (JWT)
- passlib + bcrypt
- APScheduler
- pywebpush + VAPID
- python-dotenv

### Frontend
- Streamlit
- requests
- Service Worker (`frontend/static/sw.js`)
- Push API (`frontend/static/push_init.js`)

## Структура проекта

```text
habits_project/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI приложение и эндпоинты
│   │   ├── auth.py           # JWT, хеширование паролей, current user
│   │   ├── database.py       # подключение к БД и SessionLocal
│   │   ├── models.py         # SQLAlchemy модели
│   │   ├── schemas.py        # Pydantic схемы
│   │   └── scheduler.py      # отправка push-напоминаний по расписанию
│   ├── create_tables.py      # создание таблиц в БД
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py      # Streamlit интерфейс
│   └── static/
│       ├── push_init.js      # подписка на push и отправка подписки на backend
│       ├── sw.js             # service worker для отображения уведомлений
│       └── test_sw.html      # вспомогательная страница для проверки SW
├── generate_vapid.py         # генерация VAPID ключей
├── get_public_key.py         # получение base64 публичного VAPID ключа для JS
├── vapid_private.pem
├── vapid_public.pem
└── .env
```

## Установка и запуск

### 1) Клонирование и переход в проект

```bash
git clone <repo_url>
cd habits_project
```

### 2) Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Установка зависимостей

```bash
pip install -r backend/requirements.txt
```

### 4) Настройка `.env`

Создайте файл `.env` в корне проекта и укажите переменные (пример ниже).

### 5) Подготовка базы данных

```bash
cd backend
python create_tables.py
cd ..
```

### 6) Запуск backend и frontend

Backend и frontend запускаются в разных терминалах (см. разделы ниже).

## ENV

Используемые переменные окружения:

- `DATABASE_URL` — строка подключения SQLAlchemy к PostgreSQL.
- `secret_key` — ключ для подписи JWT (используется в `backend/app/auth.py`).
- `VAPID_PRIVATE_KEY` — приватный VAPID ключ.
- `VAPID_PUBLIC_KEY` — публичный VAPID ключ.
- `VAPID_CLAIM_EMAIL` — email claim для web push.


## База данных

### Используемые таблицы
- `users`
- `habits`
- `habit_completions`
- `push_subscriptions`

### Создание таблиц

```bash
cd backend
python create_tables.py
```

Скрипт создает таблицы через `Base.metadata.create_all(bind=engine)`.

## Запуск backend/frontend

### Запуск backend (FastAPI, порт 8001)

```bash
uvicorn backend.app.main:app --reload --port 8001
```

Проверка:
- `http://127.0.0.1:8001/health` -> `{"status":"ok"}`
- `http://127.0.0.1:8001/docs` -> Swagger UI

### Запуск frontend (Streamlit)

```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

По умолчанию frontend общается с backend по `http://127.0.0.1:8001`.

## Push-уведомления и VAPID

### Как это работает

1. Пользователь нажимает кнопку "Включить уведомления" в Streamlit UI.
2. JS (`push_init.js`) регистрирует service worker (`sw.js`) и создает push-подписку в браузере.
3. Подписка отправляется на backend в `/api/push-subscribe` (с JWT).
4. Scheduler (`backend/app/scheduler.py`) раз в минуту проверяет привычки с временем напоминания и отправляет Web Push.

### Ключи VAPID

- Генерация ключей:
  ```bash
  python generate_vapid.py
  ```
- Получение публичного ключа в формате для JS:
  ```bash
  python get_public_key.py
  ```
- Важно: `publicVapidKey` в `frontend/static/push_init.js` должен соответствовать актуальному приватному ключу `vapid_private.pem`, который используется backend.

## API эндпоинты

Ниже перечислены фактические эндпоинты из `backend/app/main.py`.

### Служебные

- `GET /` — приветственное сообщение.
- `GET /health` — проверка состояния API.

### Авторизация

- `POST /auth/register` — регистрация пользователя.
  - Body: `{ "email": "user@example.com", "password": "secret" }`
- `POST /auth/login` — логин и получение JWT.
  - Body: `{ "email": "user@example.com", "password": "secret" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`

### Привычки (требуется Bearer токен)

- `POST /habits` — создать привычку.
  - Body: `{ "name": "...", "description": "...", "reminder_time": "HH:MM:SS", "days_of_week": "mon,wed,fri" }`
- `GET /habits` — получить список привычек текущего пользователя.
- `POST /habits/{habit_id}/complete` — отметить привычку выполненной сегодня.

### Профиль (требуется Bearer токен)

- `GET /user/me` — получить `email`, `total_points`, `level`.

### Push (требуется Bearer токен)

- `POST /api/push-subscribe` — сохранить push-подписку.
  - Body: объект Web Push subscription (`endpoint`, `keys.auth`, `keys.p256dh`).
- `POST /api/push-unsubscribe` — удалить push-подписку по endpoint.

## Геймификация

Логика в `POST /habits/{habit_id}/complete`:

- За выполнение привычки начисляется `5` очков.
- Повторная отметка в тот же день очки не добавляет (`Habit already completed today`).
- Очки суммируются в `users.total_points`.
- Уровень рассчитывается как: `level = total_points // 100 + 1`.
- При достижении нового уровня в ответ добавляется сообщение о повышении.

## Примеры curl

### Регистрация

```bash
curl -X POST "http://127.0.0.1:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}'
```

### Логин

```bash
curl -X POST "http://127.0.0.1:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}'
```

### Создание привычки

```bash
curl -X POST "http://127.0.0.1:8001/habits" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"name":"Пить воду","description":"2 литра в день","reminder_time":"09:00:00","days_of_week":"mon,tue,wed,thu,fri"}'
```

### Список привычек

```bash
curl -X GET "http://127.0.0.1:8001/habits" \
  -H "Authorization: Bearer <TOKEN>"
```

### Отметить выполнение

```bash
curl -X POST "http://127.0.0.1:8001/habits/1/complete" \
  -H "Authorization: Bearer <TOKEN>"
```

### Профиль пользователя

```bash
curl -X GET "http://127.0.0.1:8001/user/me" \
  -H "Authorization: Bearer <TOKEN>"
```

### Push subscribe

```bash
curl -X POST "http://127.0.0.1:8001/api/push-subscribe" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"endpoint":"https://example.push.service/...","keys":{"auth":"...","p256dh":"..."}}'
```

## Troubleshooting

- `401 Unauthorized` на защищенных эндпоинтах:
  - проверьте заголовок `Authorization: Bearer <TOKEN>`;
  - получите новый токен через `/auth/login`.
- Ошибка подключения к БД:
  - проверьте `DATABASE_URL`, доступность PostgreSQL и порт.
- Таблицы не созданы:
  - выполните `python backend/create_tables.py`.
- Push не работает:
  - убедитесь, что браузер поддерживает Service Worker и Push API;
  - разрешите уведомления для сайта;
  - проверьте соответствие VAPID ключей между frontend и backend;
  - проверьте, что backend запущен и scheduler активен.
- Уведомления не приходят по времени:
  - в привычке должен быть установлен `reminder_time`;
  - scheduler проверяет совпадение по текущим минутам, с учетом `days_of_week`.

## Безопасность

- Не храните реальные секреты и приватные ключи в публичном репозитории.
- Исключите `.env`, `vapid_private.pem`, токены и дампы БД через `.gitignore`.
- Ограничьте CORS `allow_origins` в production (сейчас разрешено `*`).
- Используйте HTTPS в production, особенно для Web Push и JWT.
- Регулярно ротируйте `secret_key` и VAPID ключи.
- Добавьте ограничение частоты запросов (`rate limiting`) для auth-эндпоинтов.

## Roadmap

- CRUD для привычек (обновление и удаление).
- Более гибкая модель расписаний (RRULE/календарь).
- История выполнения с визуализацией (графики, streaks).
- Ролевой доступ и админ-панель.
- Docker Compose для локального запуска (backend + db + frontend).
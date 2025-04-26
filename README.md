# Posts Feed Application

Веб-приложение для создания и просмотра постов с гибридным хранилищем данных (SQLite/PostgreSQL, MongoDB и Redis).

## Требования

- Python 3.8 или выше
- SQLite (встроен в Python) или PostgreSQL (для production)
- MongoDB
- Redis

## Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd posts-feed
```

2. Создайте виртуальное окружение и активируйте его:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка окружения

1. Создайте файл `.env` в корневой директории проекта со следующими параметрами:

```
# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_secret_key_here

# База данных (SQLite по умолчанию)
DATABASE_URL=sqlite:///app.db

# Для production используйте PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=posts_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

2. Замените значения параметров на ваши собственные:
   - `SECRET_KEY`: Случайная строка для безопасности сессий
   - `DATABASE_URL`: 
     - Для разработки: оставьте значение по умолчанию для SQLite
     - Для production: URL для подключения к PostgreSQL (замените username, password и dbname)
   - `MONGO_URI`: URI для подключения к MongoDB
   - `MONGO_DB`: Имя базы данных MongoDB
   - `REDIS_HOST`: Хост Redis сервера
   - `REDIS_PORT`: Порт Redis сервера

## Запуск приложения

```bash
# Запуск в режиме разработки
flask run --debug

# Или
python app.py
```

## Структура проекта

```
posts-feed/
├── app.py                  # Основной файл приложения
├── requirements.txt        # Зависимости проекта
├── .env                    # Конфигурация окружения
├── database/               # Модули для работы с базами данных
│   ├── __init__.py
│   ├── init_db.py          # Инициализация баз данных
│   ├── repositories.py     # Репозитории для работы с данными
│   └── users.py            # Сервис для работы с пользователями
├── models/                 # Модели данных
│   ├── __init__.py
│   ├── post.py             # Модель поста
│   └── user.py             # Модель пользователя
├── templates/              # HTML шаблоны
│   ├── base.html           # Базовый шаблон
│   ├── feed.html           # Страница ленты постов
│   ├── login.html          # Страница входа
│   └── register.html       # Страница регистрации
├── static/                 # Статические файлы
│   └── js/                 # JavaScript файлы
└── utils/                  # Утилиты
    ├── __init__.py
    └── config.py           # Конфигурация приложения
```

## Примечания

- Приложение использует гибридное хранилище данных:
  - SQLite (по умолчанию) или PostgreSQL (для production) для хранения информации о пользователях
  - MongoDB для хранения постов
  - Redis для кэширования
- Для разработки достаточно SQLite, который встроен в Python
- Для production рекомендуется использовать PostgreSQL из-за его надежности и производительности
- Для корректной работы необходимо настроить MongoDB и Redis
import os
from datetime import date
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Берем токен из переменной окружения BOT_TOKEN
TOKEN = os.getenv("BOT_TOKEN")

# --- НАСТРОЙКИ БАЗЫ ДАННЫХ ---
DB_CONFIG = {
    "dbname": "zhara_db",
    "user": "postgres",
    "password": "postgres",  # Если при сбросе пароля вы ставили другой, укажите его тут
    "host": "localhost",
    "port": "5432"
}

# Список тех, кому будут приходить заявки (без @)
RECIPIENTS = [1556819688, 1606744507]

# Список песен (каталог)
SONGS = [
    {"id": 1, "title": "Ненавижу(дорн)", "duration": 3.5, "price": 3000,
     "video_id": "BAACAgIAAxkBAAODauEK0FDQHkpvl7VYZvBQpi3LvUUAAneYAAJ9WnhIrJbS5c8U23w9BA"},
    {"id": 2, "title": "Кукла колдуна (Король и Шут)", "duration": 4.0, "price": 3500,
     "video_id": "BAACAgIAAxkBAAOLauEMgCjQ9AAB90KikWWJI0onHaJAAAJ1mAACfVp4SECKP6WLNsiJPQQ"},
    {"id": 3, "title": "хали гали", "duration": 4.2, "price": 3500,
     "video_id": "BAACAgIAAxkBAAOHauELloZRIOXatUUlqE6Lck4eUMsAAnqYAAJ9WnhIu39k8rANLF49BA"},
    {"id": 4, "title": "он тебя целует", "duration": 3.8, "price": 3000,
     "video_id": "BAACAgIAAxkBAAOJauEMMiSaXl5yRT0WNvYeYsxA4FIAAomYAAJ9WnhI2OWJTH6NbGY9BA"},
    {"id": 5, "title": "Танцы (Сплин)", "duration": 4.5, "price": 4000,
     "video_id": "BAACAgIAAxkBAAONauEMlupRIXvwww5fLxHWTmxwBt0AAnKYAAJ9WnhIX2tAek_6aBg9BA"},
    {"id": 99, "title": "🎸 Своя песня на заказ", "duration": 5.0, "price": 10000, "video_id": None},
]

# Список ID ваших видео в Telegram
VIDEOS = [
    "BAACAgIAAxkBAAODauEK0FDQHkpvl7VYZvBQpi3LvUUAAneYAAJ9WnhIrJbS5c8U23w9BA",
    "BAACAgIAAxkBAAOHauELloZRIOXatUUlqE6Lck4eUMsAAnqYAAJ9WnhIu39k8rANLF49BA",
    "BAACAgIAAxkBAAOJauEMMiSaXl5yRT0WNvYeYsxA4FIAAomYAAJ9WnhI2OWJTH6NbGY9BA",
    "BAACAgIAAxkBAAOLauEMgCjQ9AAB90KikWWJI0onHaJAAAJ1mAACfVp4SECKP6WLNsiJPQQ",
    "BAACAgIAAxkBAAONauEMlupRIXvwww5fLxHWTmxwBt0AAnKYAAJ9WnhIX2tAek_6aBg9BA"
]

# Занятые даты (формат "ГГГГ-ММ-ДД")
BUSY_DATES = [
    # "2026-11-15",
    # "2026-12-31",
]

# Периоды с наценкой за высокий сезон (Начало, Конец, Коэффициент)
HOLIDAY_PERIODS = [
    (date(2026, 12, 15), date(2026, 12, 30), 2.0),
    (date(2026, 12, 31), date(2027, 1, 5), 2.5),
]

# Скидка на будни (0.9 означает скидку 10% от базовой цены)
WEEKDAY_DISCOUNT = 0.9

# Коэффициенты срочности (в зависимости от того, сколько дней осталось до даты)
URGENCY_RATES = {
    "very_urgent": 2.5,
    "urgent": 1.5,
    "standard": 1.0,
    "early_bird": 0.85,
}

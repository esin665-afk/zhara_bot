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
    {"id": 1, "title": "Гречка - Люби меня", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 2, "title": "Хали-Гали - Леприконсы", "duration": 3.5, "price": 3000, "video_id":
        "BAACAgIAAxkBAAOHauELloZRIOXatUUlqE6Lck4eUMsAAnqYAAJ9WnhIu39k8rANLF49BA"},
    {"id": 3, "title": "МУМИЙ ТРОЛЛЬ - Владивосток 2000", "duration": 4.0, "price": 3500, "video_id": None},
    {"id": 4, "title": "МУМИЙ ТРОЛЛЬ - Невеста", "duration": 3.8, "price": 3000, "video_id": None},
    {"id": 5, "title": "МУМИЙ ТРОЛЛЬ - Утекай", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 6, "title": "Гречка - Твои руки", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 7, "title": "Штрудель - Седая ночь", "duration": 4.0, "price": 3500, "video_id": None},
    {"id": 8, "title": "Maneskin - Beggin", "duration": 3.5, "price": 3500, "video_id": None},
    {"id": 9, "title": "Серебро - Между нами", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 10, "title": "Him - Wicked Game", "duration": 4.0, "price": 3500, "video_id": None},
    {"id": 11, "title": "Звери - Все, что тебя касается", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 12, "title": "Руки Вверх - Он тебя целует", "duration": 3.5, "price": 3000, "video_id":
        "BAACAgIAAxkBAAOJauEMMiSaXl5yRT0WNvYeYsxA4FIAAomYAAJ9WnhI2OWJTH6NbGY9BA"},
    {"id": 13, "title": "Звери - Танцуй", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 14, "title": "Иван Дорн - Ненавижу", "duration": 3.5, "price": 3000, "video_id":
        "BAACAgIAAxkBAAODauEK0FDQHkpvl7VYZvBQpi3LvUUAAneYAAJ9WnhIrJbS5c8U23w9BA"},
    {"id": 15, "title": "Банд'Эрос - Танцы", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 16, "title": "Мальбэк - Сюзanna", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 17, "title": "Шура - Ты не верь слезам", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 18, "title": "Елка - На большом воздушном шаре", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 19, "title": "Потап и Настя - Хуторянка", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 20, "title": "IOWA - Улыбайся", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 21, "title": "Леонид Агутин - Хоп Хей Лала Лей", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 22, "title": "Billie Eilish - Bad Guy", "duration": 3.0, "price": 3000, "video_id": None},
    {"id": 23, "title": "Wicked Game", "duration": 4.0, "price": 3500, "video_id": None},
    {"id": 24, "title": "KISH - Кукла колдуна", "duration": 4.0, "price": 3500, "video_id":
        "BAACAgIAAxkBAAOLauEMgCjQ9AAB90KikWWJI0onHaJAAAJ1mAACfVp4SECKP6WLNsiJPQQ"},
    {"id": 25, "title": "KISH - Лесник", "duration": 4.0, "price": 3500, "video_id": None},
    {"id": 26, "title": "Zoya - Skalolaz", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 27, "title": "Linkin Park - Люби меня", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 28, "title": "Хolidayboy - Пожары", "duration": 3.5, "price": 3000, "video_id": None},
    {"id": 29, "title": "Nirvana - Smells Like Teen Spirit", "duration": 4.5, "price": 4000, "video_id": None},
    {"id": 30, "title": "Мишель - Посмотри", "duration": 3.5, "price": 3000,
     "video_id": "BAACAgIAAxkBAAONauEMlupRIXvwww5fLxHWTmxwBt0AAnKYAAJ9WnhIX2tAek_6aBg9BA"},
    {"id": 31, "title": "Земляне - Трава у дома", "duration": 4.0, "price": 3500, "video_id": None},

    # Своя песня на заказ
    {"id": 99, "title": "🎸 Своя песня на заказ", "duration": 5.0, "price": 10000, "video_id": None}
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

TIME_MACHINE_VIDEO = "BAACAgIAAxkBAAIBu2rlnJkn3agIcz1H5wABUSyPnPuHkAACJqsAAhk4MEuSlGr7HPkaiD0E"

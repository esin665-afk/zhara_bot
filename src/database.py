import psycopg2
from config import DB_CONFIG


def get_connection():
    """Подключение к базе данных."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Создает таблицы для песен и заказов, если их еще нет."""
    conn = get_connection()
    cur = conn.cursor()

    # Таблица для хранения заказов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(100),
            username VARCHAR(100),
            event_date VARCHAR(50),
            total_price INT,
            total_time FLOAT,
            songs_list TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ База данных готова к работе!")


def save_order(user_name, username, event_date, total_price, total_time, songs_list):
    """Сохраняет новый заказ в базу."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_name, username, event_date, total_price, total_time, songs_list)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_name, username, event_date, total_price, total_time, songs_list))
    conn.commit()
    cur.close()
    conn.close()
    print(f"💾 Заказ от {user_name} сохранен в БД!")

import psycopg2
from config import DB_CONFIG


def get_connection():
    """Подключение к базе данных."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Создает таблицы users и orders."""
    conn = get_connection()
    cur = conn.cursor()

    # 1. Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            first_name VARCHAR(100),
            username VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Таблица заказов (связываем с users)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
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


def get_or_create_user(telegram_id, first_name, username):
    """Ищет пользователя по Telegram ID, если нет — создает и возвращает его ID в базе."""
    conn = get_connection()
    cur = conn.cursor()

    # Ищем пользователя
    cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    row = cur.fetchone()

    if row:
        user_id = row[0]
    else:
        # Если нет, создаем
        cur.execute(
            "INSERT INTO users (telegram_id, first_name, username) VALUES (%s, %s, %s) RETURNING id",
            (telegram_id, first_name, username)
        )
        user_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return user_id


def save_order(user_id, event_date, total_price, total_time, songs_list):
    """Сохраняет новый заказ в базу для конкретного пользователя."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, event_date, total_price, total_time, songs_list)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, event_date, total_price, total_time, songs_list))
    conn.commit()
    cur.close()
    conn.close()
    print(f"💾 Заказ сохранен в БД (ID пользователя: {user_id})!")


def get_statistics():
    """Возвращает статистику по заказам из базы данных."""
    conn = get_connection()
    cur = conn.cursor()

    stats = {}

    # 1. Общее количество заказов
    cur.execute("SELECT COUNT(*) FROM orders")
    stats['total_orders'] = cur.fetchone()[0]

    # 2. Общая сумма всех заказов
    cur.execute("SELECT SUM(total_price) FROM orders")
    total_sum = cur.fetchone()[0]
    stats['total_revenue'] = total_sum if total_sum else 0

    # 3. Последние 3 заказа (тот самый JOIN)
    cur.execute("""
        SELECT u.first_name, o.event_date, o.total_price 
        FROM users u 
        JOIN orders o ON u.id = o.user_id 
        ORDER BY o.created_at DESC LIMIT 3
    """)
    stats['last_orders'] = cur.fetchall()

    cur.close()
    conn.close()
    return stats


def get_user_last_order(telegram_id):
    """Возвращает последний заказ конкретного пользователя по его Telegram ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.event_date, o.total_price, o.songs_list 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        WHERE u.telegram_id = %s 
        ORDER BY o.created_at DESC LIMIT 1
    """, (telegram_id,))

    order = cur.fetchone()
    cur.close()
    conn.close()
    return order


def init_songs_db(songs_list):
    """Создает таблицы песен и связывает их с заказами, заполняет из config."""
    conn = get_connection()
    cur = conn.cursor()

    # Таблица песен
    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) UNIQUE NOT NULL,
            price INT NOT NULL,
            duration FLOAT NOT NULL
        );
    """)

    # Таблица связи (какие песни в каком заказе)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_songs (
            order_id INT REFERENCES orders(id) ON DELETE CASCADE,
            song_id INT REFERENCES songs(id) ON DELETE CASCADE,
            PRIMARY KEY (order_id, song_id)
        );
    """)

    # Заполняем таблицу songs из config.py (если их там еще нет)
    for song in songs_list:
        cur.execute("SELECT id FROM songs WHERE title = %s", (song["title"],))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO songs (title, price, duration) VALUES (%s, %s, %s)",
                (song["title"], song["price"], song["duration"])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ База данных песен готова!")


def save_order_with_songs(user_id, event_date, total_price, total_time, songs_list_text, song_titles):
    """Сохраняет заказ и привязывает к нему конкретные песни."""
    conn = get_connection()
    cur = conn.cursor()

    # Сохраняем сам заказ
    cur.execute("""
        INSERT INTO orders (user_id, event_date, total_price, total_time, songs_list)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (user_id, event_date, total_price, total_time, songs_list_text))
    order_id = cur.fetchone()[0]

    # Привязываем песни к заказу (через таблицу order_songs)
    for title in song_titles:
        cur.execute("SELECT id FROM songs WHERE title = %s", (title,))
        song_row = cur.fetchone()
        if song_row:
            song_id = song_row[0]
            cur.execute(
                "INSERT INTO order_songs (order_id, song_id) VALUES (%s, %s)",
                (order_id, song_id)
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"💾 Заказ сохранен в БД с песнями (User ID: {user_id})!")


def get_top_songs():
    """Возвращает топ-5 самых популярных песен (используем INNER JOIN из урока!)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.title, COUNT(os.order_id) as times_ordered
        FROM songs s
        INNER JOIN order_songs os ON s.id = os.song_id
        GROUP BY s.title
        ORDER BY times_ordered DESC
        LIMIT 5
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_unordered_songs():
    """Возвращает список песен, которые ни разу не заказывали (LEFT JOIN)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.title
        FROM songs s
        LEFT JOIN order_songs os ON s.id = os.song_id
        WHERE os.order_id IS NULL
        ORDER BY s.title ASC
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()

    # Возвращаем простой список строк (названий песен)
    return [row[0] for row in result]

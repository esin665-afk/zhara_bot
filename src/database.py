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

    cur.execute("SELECT COUNT(*) FROM orders")
    stats['total_orders'] = cur.fetchone()[0]

    cur.execute("SELECT SUM(total_price) FROM orders")
    total_sum = cur.fetchone()[0]
    stats['total_revenue'] = total_sum if total_sum else 0

    # НОВЫЙ ЗАПРОС: собираем песни на лету с помощью STRING_AGG
    cur.execute("""
        SELECT u.first_name, o.event_date, o.total_price, 
               STRING_AGG(s.title, ', ') as songs 
        FROM users u 
        JOIN orders o ON u.id = o.user_id 
        LEFT JOIN order_songs os ON o.id = os.order_id
        LEFT JOIN songs s ON os.song_id = s.id
        GROUP BY u.first_name, o.event_date, o.total_price, o.created_at
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
        SELECT o.event_date, o.total_price, STRING_AGG(s.title, ', ') as songs
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        LEFT JOIN order_songs os ON o.id = os.order_id
        LEFT JOIN songs s ON os.song_id = s.id
        WHERE u.telegram_id = %s 
        GROUP BY o.id, o.event_date, o.total_price, o.created_at
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


def save_order_with_songs(user_id, event_date, total_price, total_time, song_titles):
    """Сохраняет заказ и привязывает к нему конкретные песни."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders (user_id, event_date, total_price, total_time)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (user_id, event_date, total_price, total_time))
    order_id = cur.fetchone()[0]

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
    print(f"💾 Заказ сохранен с песнями (User ID: {user_id})!")


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


def get_above_average_orders():
    """Возвращает заказы, стоимость которых выше среднего чека (используем подзапрос)."""
    conn = get_connection()
    cur = conn.cursor()

    # Тот самый подзапрос: WHERE total_price > (SELECT AVG(...))
    cur.execute("""
        SELECT u.first_name, o.event_date, o.total_price 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.total_price > (SELECT AVG(total_price) FROM orders)
        ORDER BY o.total_price DESC
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_sleeping_users():
    """Возвращает пользователей, которые есть в базе, но ни разу не делали заказ (NOT EXISTS)."""
    conn = get_connection()
    cur = conn.cursor()

    # Используем NOT EXISTS для поиска "спящих" клиентов
    cur.execute("""
        SELECT u.telegram_id, u.first_name, u.username 
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM orders o WHERE o.user_id = u.id
        )
        ORDER BY u.created_at DESC
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_fast_orders():
    """Возвращает заказы, сделанные в тот же день, что и регистрация (JOIN + WHERE)."""
    conn = get_connection()
    cur = conn.cursor()

    # Тот самый паттерн: JOIN + сравнение колонок в WHERE
    cur.execute("""
        SELECT u.first_name, o.total_price, o.event_date 
        FROM users u
        INNER JOIN orders o ON u.id = o.user_id
        WHERE DATE(u.created_at) = DATE(o.created_at)
        ORDER BY o.total_price DESC
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_db_audit():
    """Аудит базы данных: ищет пользователей без заказов и заказы без пользователей (FULL OUTER JOIN)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.first_name, o.event_date, u.id, o.id
        FROM users u
        FULL OUTER JOIN orders o ON u.id = o.user_id
        WHERE u.id IS NULL OR o.id IS NULL
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_monthly_stats():
    """Возвращает статистику среднего чека по месяцам (GROUP BY + HAVING)."""
    conn = get_connection()
    cur = conn.cursor()

    # Берем месяц из даты (формат DD.MM.YYYY -> берем символы с 4-го по 5-й)
    cur.execute("""
        SELECT substring(event_date from 4 for 2) AS month, 
               COUNT(id) as orders_count, 
               AVG(total_price) as avg_price
        FROM orders
        GROUP BY month
        HAVING COUNT(id) >= 1
        ORDER BY month
    """)

    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def add_phone_column():
    """Добавляет колонку phone в таблицу users, если её еще нет (ALTER TABLE)."""
    conn = get_connection()
    cur = conn.cursor()

    # Команда DDL: добавляем колонку
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Колонка phone добавлена в таблицу users!")


def update_user_phone(telegram_id, phone):
    """Сохраняет номер телефона пользователя в базу."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET phone = %s WHERE telegram_id = %s",
        (phone, telegram_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"📱 Телефон {phone} сохранен для пользователя {telegram_id}!")


def add_check_constraints():
    """Добавляет логические ограничения (CHECK) в таблицы."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Цена в заказе не может быть отрицательной
        cur.execute("""
            ALTER TABLE orders 
            ADD CONSTRAINT check_total_price_positive 
            CHECK (total_price >= 0);
        """)

        # 2. Цена песни должна быть строго больше нуля
        cur.execute("""
            ALTER TABLE songs 
            ADD CONSTRAINT check_song_price_positive 
            CHECK (price > 0);
        """)

        # 3. Длительность песни должна быть больше нуля
        cur.execute("""
            ALTER TABLE songs 
            ADD CONSTRAINT check_song_duration_positive 
            CHECK (duration > 0);
        """)

        conn.commit()
        print("✅ Логические ограничения (CHECK) успешно добавлены!")

    except Exception as e:
        # Если ограничения уже добавлены, база выдаст ошибку, мы её перехватим
        conn.rollback()
        print(f"ℹ️ Ограничения уже существуют или произошла ошибка: {e}")

    cur.close()
    conn.close()


def drop_songs_list_column():
    """Удаляет колонку songs_list из orders, так как мы перешли на нормальную связь order_songs."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("ALTER TABLE orders DROP COLUMN IF EXISTS songs_list;")
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Колонка songs_list удалена (база нормализована)!")

import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from src.handlers import register_handlers

# 1. ДОБАВЬТЕ ЭТУ СТРОКУ (импорт функции создания таблиц)
from src.database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    print("Бот запущен! Идем в Telegram и проверяем...")

    # 2. ДОБАВЬТЕ ЭТУ СТРОКУ (создаем таблицы в базе данных перед запуском)
    init_db()

    # Создаем бота и диспетчер
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрируем все обработчики из модуля handlers.py
    register_handlers(dp)

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")

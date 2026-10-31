import logging
import asyncio
from aiogram import Bot, Dispatcher, types  # <-- ДОБАВЬТЕ types ВОТ СЮДА
from config import TOKEN
from src.handlers import register_handlers
from src.admin import register_admin_handlers
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

    # Регистрируем админ-панель
    register_admin_handlers(dp)  # <-- ДОБАВИТЬ ЭТУ СТРОКУ

    # # ВРЕМЕННЫЙ ЛОВЕЦ ВИДЕО
    # @dp.message(lambda message: message.video is not None)
    # async def get_video_id(message: types.Message):
    #     # Выводим в консоль
    #     print(f"\n=== ВАШ ID ВИДЕО ===\n{message.video.file_id}\n====================\n")
    #     # Присылаем в чат
    #     await message.answer(f"✅ ID вашего видео:\n`{message.video.file_id}`", parse_mode="Markdown")

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")

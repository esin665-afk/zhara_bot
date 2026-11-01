import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from config import TOKEN, SONGS
from src.handlers import register_handlers
from src.admin import register_admin_handlers
from aiogram.types import Message
from src.database import init_db, init_songs_db, add_phone_column, update_user_phone
from src.keyboards import get_main_menu  # <-- ДОБАВЛЕН ИМПОРТ КЛАВИАТУРЫ

logging.basicConfig(level=logging.INFO)


async def main():
    print("Бот запущен! Идем в Telegram и проверяем...")

    init_db()
    add_phone_column()
    init_songs_db(SONGS)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    register_handlers(dp)
    register_admin_handlers(dp)

    @dp.message(lambda message: message.contact is not None)
    async def handle_contact(message: Message):
        phone = message.contact.phone_number
        user_id = message.from_user.id

        update_user_phone(user_id, phone)

        await message.answer(
            "✅ Спасибо! Телефон сохранен. Менеджер свяжется с вами в ближайшее время.",
            reply_markup=get_main_menu()
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")

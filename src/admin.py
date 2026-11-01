from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from src.database import get_statistics, get_top_songs
from src.keyboards import get_admin_menu, get_main_menu

# Список ID тех, кому разрешена команда /admin (ваш и менеджера)
ADMIN_IDS = [1556819688, 1606744507]


def register_admin_handlers(dp):
    """Регистрация обработчиков для админ-панели."""

    @dp.message(Command("admin"))
    async def admin_panel(message: types.Message):
        # Проверка доступа
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("У вас нет доступа к этой команде.")
            return

        await message.answer(
            "👨‍💻 <b>Админ-панель бота «ЖАРА»</b>\nВыберите действие:",
            parse_mode="HTML",
            reply_markup=get_admin_menu()
        )

    @dp.callback_query(lambda c: c.data == "admin_stats")
    async def admin_stats_panel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            return

        await callback.answer()
        stats = get_statistics()

        text = "📊 **Статистика бота «ЖАРА»**\n\n"
        text += f"📦 Всего заказов: {stats['total_orders']}\n"
        text += f"💰 Общая выручка: {stats['total_revenue']} руб.\n\n"

        text += "🕒 **Последние заказы:**\n"
        if not stats['last_orders']:
            text += "Пока нет заказов."
        else:
            for order in stats['last_orders']:
                text += f"- {order[0]} | {order[1]} | {order[2]} руб.\n"

        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_admin_menu())

    @dp.callback_query(lambda c: c.data == "admin_top_songs")
    async def admin_top_songs_panel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            return

        await callback.answer()
        top_songs = get_top_songs()

        if not top_songs:
            await callback.message.answer("Пока нет заказов, чтобы составить топ песен.", reply_markup=get_admin_menu())
            return

        text = "🏆 <b>ТОП-5 САМЫХ ЗАКАЗЫВАЕМЫХ ПЕСЕН:</b>\n\n"
        for i, (title, count) in enumerate(top_songs, start=1):
            text += f"{i}. {title} — <b>{count}</b> раз(а)\n"

        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_admin_menu())

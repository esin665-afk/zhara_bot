from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from src.database import (
    get_statistics, get_top_songs, get_unordered_songs,
    get_above_average_orders, get_sleeping_users
)
from src.keyboards import get_admin_menu

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

    @dp.callback_query(lambda c: c.data == "admin_unordered")
    async def admin_unordered_panel(callback: CallbackQuery):
        # Проверка доступа
        if callback.from_user.id not in ADMIN_IDS:
            return

        await callback.answer()

        # Получаем список песен, которые никто не заказывал
        unordered_songs = get_unordered_songs()

        if not unordered_songs:
            text = "🎉 Отличные новости! Все песни из каталога хотя бы раз, но заказывали."
            await callback.message.answer(text, reply_markup=get_admin_menu())
            return

        text = "📉 <b>ПЕСНИ, КОТОРЫЕ НИ РАЗУ НЕ ЗАКАЗЫВАЛИ:</b>\n\n"
        for song in unordered_songs:
            text += f"- {song}\n"

        text += "\n<i>Возможно, стоит убрать их из бота или заменить на новые?</i>"

        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_admin_menu())

    @dp.callback_query(lambda c: c.data == "admin_above_avg")
    async def admin_above_avg_panel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            return

        await callback.answer()

        # Вызываем функцию с подзапросом
        above_avg = get_above_average_orders()

        if not above_avg:
            text = "Пока нет заказов, которые превышают средний чек (или заказов вообще нет)."
            await callback.message.answer(text, reply_markup=get_admin_menu())
            return

        text = "💎 <b>ЗАКАЗЫ ВЫШЕ СРЕДНЕГО ЧЕКА (VIP):</b>\n\n"
        for row in above_avg:
            # row[0] - имя клиента, row[1] - дата, row[2] - сумма
            text += f"- {row[0]} | {row[1]} | <b>{row[2]} руб.</b>\n"

        text += "\n<i>*Эти клиенты приносят основную выручку. Уделите им особое внимание!</i>"

        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_admin_menu())

    @dp.callback_query(lambda c: c.data == "admin_sleeping_users")
    async def admin_sleeping_users_panel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            return

        await callback.answer()

        # Вызываем функцию с NOT EXISTS
        sleeping_users = get_sleeping_users()

        if not sleeping_users:
            text = "🎉 Отлично! Все зарегистрированные пользователи сделали хотя бы один заказ."
            await callback.message.answer(text, reply_markup=get_admin_menu())
            return

        text = "💤 <b>СПЯЩИЕ КЛИЕНТЫ (Зашли в бота, но не заказали):</b>\n\n"
        for row in sleeping_users:
            # row[0] - telegram_id, row[1] - имя, row[2] - username
            tg_id, first_name, username = row
            username_str = f"@{username}" if username else "нет ника"
            text += f"- {first_name} ({username_str}) | ID: <code>{tg_id}</code>\n"

        text += "\n<i>*Этим клиентам можно написать первыми и предложить скидку, чтобы они сделали заказ!</i>"

        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_admin_menu())

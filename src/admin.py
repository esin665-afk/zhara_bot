from aiogram import types
from aiogram.filters import Command
from src.database import get_statistics

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

        # Получаем данные из базы (функцию добавим в database.py)
        stats = get_statistics()

        text = "📊 **Статистика бота «ЖАРА»**\n\n"
        text += f"📦 Всего заказов: {stats['total_orders']}\n"
        text += f"💰 Общая выручка: {stats['total_revenue']} руб.\n\n"

        text += "🕒 **Последние заказы:**\n"
        if not stats['last_orders']:
            text += "Пока нет заказов."
        else:
            for order in stats['last_orders']:
                # order[0] - имя, order[1] - дата, order[2] - сумма
                text += f"- {order[0]} | {order[1]} | {order[2]} руб.\n"

        await message.answer(text, parse_mode="Markdown")

import datetime
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from src.keyboards import get_main_menu
from config import (
    BUSY_DATES, HOLIDAY_PERIODS, WEEKDAY_DISCOUNT, URGENCY_RATES,
    TIME_MACHINE_VIDEO  # <-- Добавили ID видео сюда
)

user_dates = {}


def register_calendar_handlers(dp):
    @dp.callback_query(lambda c: c.data == 'book_date')
    async def show_calendar(callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(
            "📅 Выберите дату вашего мероприятия:\n(Цена зависит от дня недели и срока бронирования)",
            reply_markup=await SimpleCalendar().start_calendar()
        )

    @dp.callback_query(SimpleCalendarCallback.filter())
    async def process_calendar(callback: CallbackQuery, callback_data: dict):
        selected, selected_date = await SimpleCalendar().process_selection(callback, callback_data)

        if selected:
            selected_date = selected_date.date()
            date_str = selected_date.strftime("%Y-%m-%d")
            today = datetime.date.today()

            # 🚨 1. ПРОВЕРКА НА ПРОШЛОЕ (С ПАСХАЛКОЙ) 🚨
            if selected_date < today:
                await callback.answer()

                # Отправляем видео с шуткой
                try:
                    await callback.message.answer_video(
                        video=TIME_MACHINE_VIDEO,
                        caption=(
                            "🚨 <b>ОШИБКА ВРЕМЕННОЙ ЛИНИИ!</b> 🚨\n\n"
                            "Вы попытались заказать группу на дату, которая уже прошла.\n"
                            "К сожалению, мы пока не изобрели машину времени, чтобы поехать и сыграть для вас в прошлом. "
                            "Но если вы знаете, где достать 1.21 гигаватт и Делориан — мы готовы! 🚗⚡️\n\n"
                            "А пока, пожалуйста, выберите актуальную дату:"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Ошибка отправки видео: {e}")
                    await callback.message.answer("Ошибка временной линии! Выберите дату из будущего.")

                # Снова показываем календарь
                await callback.message.answer(
                    "📅 Выберите дату из будущего:",
                    reply_markup=await SimpleCalendar().start_calendar()
                )
                return

            # 🚨 2. ПРОВЕРКА НА ЗАНЯТОСТЬ 🚨
            if date_str in BUSY_DATES:
                await callback.message.edit_text(
                    f"❌ Увы, дата <b>{selected_date.strftime('%d.%m.%Y')}</b> уже занята.\nВыберите другую:",
                    parse_mode="HTML",
                    reply_markup=await SimpleCalendar().start_calendar()
                )
                return

            # 3. РАСЧЕТ СТОИМОСТИ (Сезон, будни, срочность)
            base_multiplier = 1.0
            status = "Стандартный день"

            for start_d, end_d, coef in HOLIDAY_PERIODS:
                if start_d <= selected_date <= end_d:
                    base_multiplier = coef
                    status = "🔥 Высокий сезон (праздники)"
                    break

            if base_multiplier == 1.0 and selected_date.weekday() in [0, 1, 2, 3]:
                base_multiplier = WEEKDAY_DISCOUNT
                status = "🎁 Скидка за будний день (Пн-Чт)"

            days_left = (selected_date - today).days

            if days_left <= 2:
                urgency = URGENCY_RATES["very_urgent"]
                status += " + 🚨 Срочный заказ"
            elif days_left <= 7:
                urgency = URGENCY_RATES["urgent"]
                status += " + ⚡ Позднее бронирование"
            elif days_left >= 30:
                urgency = URGENCY_RATES["early_bird"]
                status += " + 🐦 Ранняя бронь (Скидка!)"
            else:
                urgency = URGENCY_RATES["standard"]

            multiplier = round(base_multiplier * urgency, 2)

            # 4. СОХРАНЯЕМ И ВЫВОДИМ РЕЗУЛЬТАТ
            user_id = callback.from_user.id
            user_dates[user_id] = (selected_date.strftime('%d.%m.%Y'), multiplier, status)

            text = (
                f"✅ Дата <b>{selected_date.strftime('%d.%m.%Y')}</b> зафиксирована!\n\n"
                f"Статус: {status}\n"
                f"Итоговый коэффициент: <b>x{multiplier}</b>\n\n"
                f"Теперь при сборке сета цены будут пересчитаны с учетом этой даты. "
                f"Перейдите в «Собрать свой сет»!"
            )
            await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_main_menu())

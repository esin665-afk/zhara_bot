import datetime
from aiogram import types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from src.keyboards import get_main_menu, get_songs_menu
from config import (
    SONGS, RECIPIENTS, VIDEOS, BUSY_DATES,
    HOLIDAY_PERIODS, WEEKDAY_DISCOUNT, URGENCY_RATES
)
from src.database import save_order

# Словари для хранения данных пользователей
user_carts = {}
user_dates = {}


def register_handlers(dp):
    """Регистрация всех обработчиков."""

    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer(
            "🔥 Привет! Это бот кавер-группы «ЖАРА».\n"
            "Выбирай, что тебя интересует:",
            reply_markup=get_main_menu()
        )

    # --- ОБРАБОТЧИК КАЛЕНДАРЯ ---

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
            # 1. Превращаем DATETIME в DATE для сравнения
            selected_date = selected_date.date()
            date_str = selected_date.strftime("%Y-%m-%d")

            # 2. Проверка на занятость
            if date_str in BUSY_DATES:
                await callback.message.edit_text(
                    f"❌ Увы, дата <b>{selected_date.strftime('%d.%m.%Y')}</b> уже занята.\n"
                    "Выберите другую дату:",
                    parse_mode="HTML",
                    reply_markup=await SimpleCalendar().start_calendar()
                )
                return

            # 2. Расчет сезонного коэффициента (праздники и будни)
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

            # 3. Расчет срочности
            today = datetime.date.today()
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

            # Итоговый коэффициент
            multiplier = round(base_multiplier * urgency, 2)

            # Сохраняем для пользователя
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

    # --- ОБРАБОТЧИКИ КНОПОК МЕНЮ ---

    @dp.callback_query()
    async def button_handler(callback: CallbackQuery):
        data = callback.data
        user_id = callback.from_user.id

        if user_id not in user_carts:
            user_carts[user_id] = []

        if data == "afisha":
            await callback.answer()
            text = "🎸 Ближайшие выступления:\n\n📅 15 сентября — Бар «Old gentleman»\n📅 22 сентября — Паб «Кэрролл»\nПодробности в соцсетях!"
            await callback.message.edit_text(text=text, reply_markup=get_main_menu())

        elif data == "video":
            await callback.answer()
            text_vk = (
                "🎥 **Наш проморолик и соцсети:**\n\n"
                "Смотрите полную версию по ссылке:\n"
                "https://vkvideo.ru/video-128877586_456239060?t=5m15s\n"
                "Наш ВК: https://vk.ru/zhara_62\n\n"
                "А вот и короткое видео прямо здесь 👇"
            )
            await callback.message.edit_text(text=text_vk)

            if VIDEOS:
                for video_id in VIDEOS:
                    try:
                        await callback.message.answer_video(video=video_id)
                    except Exception as e:
                        print(f"Ошибка отправки видео: {e}")
            await callback.message.answer("🔥 Главное меню:", reply_markup=get_main_menu())

        elif data == "contacts":
            await callback.answer()
            text = "📞 Свяжись с нами:\nМенеджер: +7 910 616-47-60\n\nПодписывайся на нашу группу ВК 👇"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💙 Перейти в группу ВК", url="https://vk.ru/zhara_62")],
                [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
            ])
            await callback.message.edit_text(text=text, reply_markup=keyboard)


        elif data == "set_builder":
            await callback.answer()
            user_id = callback.from_user.id
            # Проверяем, выбрана ли дата
            if user_id not in user_dates:
                # Если даты нет, отправляем обратно в календарь
                await callback.message.edit_text(
                    "⚠️ <b>Сначала выберите дату мероприятия!</b>\n\n"
                    "Без даты мы не можем рассчитать стоимость и проверить свободен ли день.",
                    parse_mode="HTML",
                    reply_markup=await SimpleCalendar().start_calendar()
                )
                return  # Прерываем выполнение, чтобы сет не открылся
            # Если дата есть, идем дальше

            user_carts[user_id] = []

            date_info = user_dates.get(user_id)

            date_str, multiplier, status = date_info

            text = (
                f"🎸 Выбери песни для своего сета:\n"
                f"📅 Дата: <b>{date_str}</b>\n"
                f"📊 Статус: {status} (x{multiplier})\n"
                f"(Корзина пуста)"
            )
            await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_songs_menu())

        elif data.startswith("add_"):
            song_id = int(data.split("_")[1])

            song = next((s for s in SONGS if s["id"] == song_id), None)

            if song:
                if song not in user_carts[user_id]:
                    user_carts[user_id].append(song)
                    await callback.answer(f"✅ Добавлено: {song['title']}", show_alert=False)
                else:
                    await callback.answer("Эта песня уже есть в сете!", show_alert=True)
                    return

                # ВАУ-ЭФФЕКТ: Если у песни есть видео, отправляем его!
                if song.get("video_id"):
                    try:
                        await callback.message.answer_video(
                            video=song["video_id"],
                            caption=f"🎸 Живое исполнение: {song['title']}"
                        )
                    except Exception as e:
                        print(f"Ошибка отправки видео песни: {e}")

                # Живой калькулятор с учетом даты
                total_duration = sum(s["duration"] for s in user_carts[user_id])

                # Получаем коэффициент пользователя
                multiplier = user_dates.get(user_id, ("", 1.0, ""))[1]
                base_price = sum(s["price"] for s in user_carts[user_id])
                total_price = int(base_price * multiplier)

                text = "🎸 Выбери песни для своего сета:\n\n🎵 В сете сейчас:\n"
                for s in user_carts[user_id]:
                    text += f"- {s['title']}\n"

                text += f"\n⏱ Время: {round(total_duration, 1)} мин."
                text += f"\n💰 Стоимость: {total_price} руб. (с учетом даты)\n"

                if total_duration > 45:
                    text += "\n⚠️ Внимание! Вы превысили стандартный лимит 45 минут!"

                text += "\n\nПродолжай выбирать или нажми 'Посчитать итог'."

                await callback.message.edit_text(
                    text=text,
                    reply_markup=callback.message.reply_markup
                )


        elif data == "clear_cart":
            await callback.answer("Корзина очищена!")

            # Очищаем корзину пользователя
            user_carts[user_id] = []

            # Показываем меню заново
            text = (
                "🎸 Твой сет очищен!\n\n"
                "Выбери песни заново:"
            )
            await callback.message.edit_text(text=text, reply_markup=get_songs_menu())


        elif data == "calculate_total":
            cart = user_carts.get(user_id, [])
            if user_id not in user_dates:
                await callback.answer("Сначала выберите дату в календаре!", show_alert=True)
                return
            if not cart:
                await callback.answer("Корзина пуста! Добавь песни.", show_alert=True)
                return

            await callback.answer()

            total_time = sum(song["duration"] for song in cart)
            multiplier = user_dates.get(user_id, ("", 1.0, ""))[1]
            base_price = sum(song["price"] for song in cart)
            total_price = int(base_price * multiplier)

            date_info = user_dates.get(user_id, ("Не выбрана", 1.0, "Стандарт"))
            date_str, _, date_status = date_info

            # Отправка заявки менеджеру
            manager_text = (
                f"🔥 **НОВАЯ ЗАЯВКА!**\n\n"
                f"Клиент: {callback.from_user.first_name} (@{callback.from_user.username})\n"
                f"📅 Дата: {date_str} ({date_status})\n"
                f"⏱ Время: {round(total_time, 1)} мин.\n"
                f"💰 Сумма: {total_price} руб.\n\n"
                f"🎵 Песни:\n"
            )
            for s in cart:
                manager_text += f"- {s['title']}\n"

            for recipient_id in RECIPIENTS:
                try:
                    await callback.bot.send_message(chat_id=recipient_id, text=manager_text)
                except Exception as e:
                    print(f"Ошибка отправки {recipient_id}: {e}")
            # СОХРАНЯЕМ ЗАКАЗ В БАЗУ ДАННЫХ
            songs_text = ", ".join([s['title'] for s in cart])
            save_order(
                user_name=callback.from_user.first_name,
                username=callback.from_user.username or "Нет ника",
                event_date=date_str,
                total_price=total_price,
                total_time=total_time,
                songs_list=songs_text
            )

            # Ответ клиенту
            text = "🎉 Твой сет собран и отправлен менеджеру!\n\n🎵 Песни:\n"
            for s in cart:
                text += f"- {s['title']}\n"
            text += f"\n📅 Дата: {date_str}\n"
            text += f"⏱ Общее время: {round(total_time, 1)} мин.\n"
            text += f"💰 Общая стоимость: {total_price} руб.\n\n"
            text += "С тобой свяжутся для уточнения деталей."

            user_carts[user_id] = []
            await callback.message.edit_text(text=text, reply_markup=get_main_menu())

        elif data == "main_menu":
            await callback.answer()
            await callback.message.edit_text("🔥 Главное меню:", reply_markup=get_main_menu())

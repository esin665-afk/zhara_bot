from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar
from src.keyboards import get_main_menu, get_songs_menu
from config import SONGS, RECIPIENTS
from src.database import get_or_create_user, save_order_with_songs
from src.handlers.calendar import user_dates
from src.pdf_generator import generate_receipt
from aiogram.types import FSInputFile
import os

user_carts = {}


def register_set_handlers(dp):
    @dp.callback_query(lambda c: c.data == "set_builder")
    async def set_builder(callback: CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id

        if user_id not in user_dates:
            # ИЗМЕНЕНО: edit_text -> answer
            await callback.message.answer(
                "⚠️ <b>Сначала выберите дату мероприятия!</b>\n\n"
                "Без даты мы не можем рассчитать стоимость и проверить свободен ли день.",
                parse_mode="HTML",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return

        user_carts[user_id] = []
        date_str, multiplier, status = user_dates.get(user_id)

        text = (
            f"🎸 Выбери песни для своего сета:\n"
            f"📅 Дата: <b>{date_str}</b>\n"
            f"📊 Статус: {status} (x{multiplier})\n"
            f"(Корзина пуста)"
        )
        # ИЗМЕНЕНО: edit_text -> answer
        await callback.message.answer(text=text, parse_mode="HTML", reply_markup=get_songs_menu())

    @dp.callback_query(lambda c: c.data.startswith("add_"))
    async def add_song(callback: CallbackQuery):
        song_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        song = next((s for s in SONGS if s["id"] == song_id), None)

        if song:
            if song not in user_carts.setdefault(user_id, []):
                user_carts[user_id].append(song)
                await callback.answer(f"✅ Добавлено: {song['title']}", show_alert=False)
            else:
                await callback.answer("Эта песня уже есть в сете!", show_alert=True)
                return

            if song.get("video_id"):
                try:
                    await callback.message.answer_video(video=song["video_id"],
                                                        caption=f"🎸 Живое исполнение: {song['title']}")
                except Exception as e:
                    print(f"Ошибка отправки видео: {e}")

            total_duration = sum(s["duration"] for s in user_carts[user_id])
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

            try:
                await callback.message.delete()
            except Exception:
                pass
            # Здесь уже был answer, оставляем как есть
            await callback.message.answer(text=text, reply_markup=callback.message.reply_markup)

    @dp.callback_query(lambda c: c.data == "clear_cart")
    async def clear_cart(callback: CallbackQuery):
        await callback.answer("Корзина очищена!")
        user_carts[callback.from_user.id] = []
        # ИЗМЕНЕНО: edit_text -> answer
        await callback.message.answer("🎸 Твой сет очищен!\n\nВыбери песни заново:", reply_markup=get_songs_menu())

    @dp.callback_query(lambda c: c.data == "calculate_total")
    async def calculate_total(callback: CallbackQuery):
        user_id = callback.from_user.id
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

        date_str, _, date_status = user_dates.get(user_id)

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

        # СОХРАНЕНИЕ В БАЗУ
        user_db_id = get_or_create_user(
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name,
            username=callback.from_user.username or "Нет ника"
        )
        songs_text = ", ".join([s['title'] for s in cart])
        song_titles = [s['title'] for s in cart]

        save_order_with_songs(
            user_id=user_db_id,
            event_date=date_str,
            total_price=total_price,
            total_time=total_time,
            songs_list_text=songs_text,
            song_titles=song_titles
        )

        text = "🎉 Твой сет собран и отправлен менеджеру!\n\n🎵 Песни:\n"
        for s in cart:
            text += f"- {s['title']}\n"
        text += f"\n📅 Дата: {date_str}\n⏱ Общее время: {round(total_time, 1)} мин.\n"
        text += f"💰 Общая стоимость: {total_price} руб.\n\nС тобой свяжутся для уточнения деталей."

        user_carts[user_id] = []

        # --- ГЕНЕРАЦИЯ И ОТПРАВКА PDF ---
        try:
            pdf_filename = generate_receipt(
                user_name=callback.from_user.first_name,
                event_date=date_str,
                songs_list=songs_text,
                total_time=total_time,
                total_price=total_price
            )
            pdf_file = FSInputFile(pdf_filename)
            await callback.message.answer_document(
                document=pdf_file,
                caption="📄 Ваш официальный чек и сет-лист. Сохраните его!"
            )
            os.remove(pdf_filename)
        except Exception as e:
            print(f"Ошибка генерации PDF: {e}")
        # --------------------------------

        # ИЗМЕНЕНО: edit_text -> answer
        await callback.message.answer(text=text, reply_markup=get_main_menu())

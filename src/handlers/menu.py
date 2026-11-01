from aiogram import types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from src.keyboards import get_main_menu
from config import VIDEOS, WELCOME_VIDEO
from src.database import get_user_last_order

def register_menu_handlers(dp):
    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer_video(
            video=WELCOME_VIDEO,
            caption="🔥 Привет! Это бот кавер-группы «ЖАРА».\nВыбирай, что тебя интересует:",
            reply_markup=get_main_menu()
        )

    @dp.callback_query(lambda c: c.data in ["afisha", "video", "contacts", "main_menu", "my_orders"])
    async def menu_handler(callback: CallbackQuery):
        data = callback.data
        await callback.answer()

        # ИСПОЛЬЗУЕМ answer ВМЕСТО edit_text
        if data == "afisha":
            text = "🎸 Ближайшие выступления:\n\n📅 15 сентября — Бар «Old gentleman»\n📅 22 сентября — Паб «Кэрролл»\nПодробности в соцсетях!"
            await callback.message.answer(text=text, reply_markup=get_main_menu())

        elif data == "video":
            text_vk = (
                "🎥 **Наш проморолик и соцсети:**\n\n"
                "Смотрите полную версию по ссылке:\n"
                "https://vkvideo.ru/video-128877586_456239060?t=5m15s\n"
                "Наш ВК: https://vk.ru/zhara_62\n\n"
                "А вот и короткое видео прямо здесь 👇"
            )
            await callback.message.answer(text=text_vk)
            if VIDEOS:
                for video_id in VIDEOS:
                    try:
                        await callback.message.answer_video(video=video_id)
                    except Exception as e:
                        print(f"Ошибка отправки видео: {e}")
            await callback.message.answer("🔥 Главное меню:", reply_markup=get_main_menu())

        elif data == "contacts":
            text = "📞 Свяжись с нами:\nМенеджер: +7 910 616-47-60\n\nПодписывайся на нашу группу ВК 👇"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💙 Перейти в группу ВК", url="https://vk.ru/zhara_62")],
                [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
            ])
            await callback.message.answer(text=text, reply_markup=keyboard)

        elif data == "my_orders":
            order = get_user_last_order(callback.from_user.id)
            if not order:
                text = "Вы пока не делали заказов 🤷‍♂️\nСамое время собрать свой первый сет!"
                await callback.message.answer(text=text, reply_markup=get_main_menu())
            else:
                date, price, songs = order
                text = (
                    f"🎫 <b>Ваш последний заказ:</b>\n\n"
                    f"📅 Дата: <b>{date}</b>\n"
                    f"💰 Сумма: <b>{price} руб.</b>\n"
                    f"🎵 Песни: {songs}\n\n"
                    f"<i>(Если нужно что-то изменить, свяжитесь с менеджером)</i>"
                )
                await callback.message.answer(text=text, parse_mode="HTML", reply_markup=get_main_menu())

        elif data == "main_menu":
            await callback.message.answer("🔥 Главное меню:", reply_markup=get_main_menu())

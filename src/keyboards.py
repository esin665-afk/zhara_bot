from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import SONGS

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton(text="🎵 Афиша", callback_data="afisha")],
        [InlineKeyboardButton(text="🎥 Видео", callback_data="video")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="💙 Мы во ВКонтакте", url="https://vk.ru/zhara_62")],
        [InlineKeyboardButton(text="📅 Выбрать дату", callback_data="book_date")], # <-- ВОТ ОНА!
        [InlineKeyboardButton(text="🎸 Собрать свой сет", callback_data="set_builder")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_songs_menu():
    """Меню с выбором песен."""
    songs_buttons = []
    for song in SONGS:
        button_text = f"{song['title']} ({song['duration']} мин) - {song['price']}₽"
        songs_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"add_{song['id']}")])

    songs_buttons.append([InlineKeyboardButton(text="✅ Посчитать итог", callback_data="calculate_total")])
    songs_buttons.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")])

    return InlineKeyboardMarkup(inline_keyboard=songs_buttons)

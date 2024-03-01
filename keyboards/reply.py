from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_registration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация на мероприятие"),
        ],
    ],
    resize_keyboard=True
)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_registration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация на мероприятие"),
        ],
    ],
    resize_keyboard=True
)


confirm_or_change_user_info_by_user = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Зарегистрироваться"),
            KeyboardButton(text="Изменить информацию")
        ],
    ],
    resize_keyboard=True
)

continue_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Продолжить"),
        ],
    ],
    resize_keyboard=True
)
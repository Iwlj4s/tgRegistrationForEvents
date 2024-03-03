from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# User #
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
            KeyboardButton(text="Изменить предыдущее поле")
        ],
    ],
    resize_keyboard=True
)


# Admin #

start_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Просмотр пользователей"),
            KeyboardButton(text="Изменить данные Пользователя"),
            KeyboardButton(text="Выйти из администратора")
        ],
    ],
    resize_keyboard=True
)

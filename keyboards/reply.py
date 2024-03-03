from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# User #
start_registration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация на мероприятие"),
            KeyboardButton(text="список мероприятий"),
        ],
    ],
    resize_keyboard=True
)


confirm_or_change_user_info_by_user = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Зарегистрироваться"),
            KeyboardButton(text="Изменить предыдущее поле"),
            KeyboardButton(text="отмена")

        ],
    ],
    resize_keyboard=True
)


# Admin #

start_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Просмотр пользователей"),
            KeyboardButton(text="Выйти из администратора")
        ],
    ],
    resize_keyboard=True
)


# KeyboardBuilder #
def get_keyboard(
        *btns: str,
        sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True)


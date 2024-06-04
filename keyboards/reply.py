from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# User #

# Start keyboard
start_registration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация"),
        ],
    ],
    resize_keyboard=True
)

# confirm registration (by user) keyboard
confirm_or_change_user_info_by_user = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зарегистрироваться")],

        [KeyboardButton(text="Изменить предыдущее поле")],

        [KeyboardButton(text="отмена")],
    ],
    resize_keyboard=True
)

# If user have registration keyboard
after_registration_user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация на мероприятие"),
            KeyboardButton(text="Отписаться от мероприятия"),
        ],

        [KeyboardButton(text="Посмотреть пользователя")],

        [KeyboardButton(text="Список мероприятий")]
    ],
    resize_keyboard=True
)

# Admin #

# Start admin keyboard
start_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Просмотр пользователей")],

        [
            KeyboardButton(text="Просмотр мероприятий"),
            KeyboardButton(text="Добавить мероприятие")
        ],

        [KeyboardButton(text="Добавить администратора")],

        [KeyboardButton(text="Выйти из администратора")]
    ],
    resize_keyboard=True
)

# Cancel or Back for User Change admin keyboard
cancel_or_back_user = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить предыдущее поле")],

        [KeyboardButton(text="отмена")]
    ],
    resize_keyboard=True
)

# Cancel or Back for User Change admin keyboard
cancel_or_back_for_user_change_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="[Admin-user] Изменить предыдущее поле")],

        [KeyboardButton(text="[Admin-user] Пропустить поле")],

        [KeyboardButton(text="[Admin] отмена")]
    ],
    resize_keyboard=True
)

# Cancel or Back for Add Event admin keyboard
cancel_or_back_for_add_event_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="[Admin-event] Изменить предыдущее поле")],

        [KeyboardButton(text="[Admin-event] Пропустить поле")],

        [KeyboardButton(text="[Admin] отмена")]
    ],
    resize_keyboard=True
)

# Confirm changing info (by admin) keyboard
confirm_or_change_user_info_by_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить информацию")],

        [KeyboardButton(text="[Admin-user] Изменить предыдущее поле")],

        [KeyboardButton(text="[Admin] отмена")]
    ],
    resize_keyboard=True
)

# Confirm or change event info
confirm_or_change_event_info_by_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить мероприятие")],

        [KeyboardButton(text="[Admin-event] Изменить предыдущее поле"),],

        [KeyboardButton(text="[Admin] отмена")]
    ],
    resize_keyboard=True
)

# Cancel or Back for User Change admin keyboard
cancel_or_back_for_admin_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="[Admin-admin] Изменить предыдущее поле")],

        [KeyboardButton(text="[Admin] отмена")]
    ],
    resize_keyboard=True
)

# Confirm or change admin info
confirm_or_change_admin_info_by_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить администратора")],

        [KeyboardButton(text="[Admin-admin] Изменить предыдущее поле")],

        [KeyboardButton(text="[Admin] отмена")]
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

# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.types import ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message

# SqlAlchemy Imports #
from sqlalchemy.ext.asyncio import AsyncSession

# My Imports #
from keyboards.reply import start_registration_keyboard, confirm_or_change_user_info_by_user

from user_data.get_user_info import get_user_info

from database.orm_query import orm_user_add_info

user_registration_router = Router()


# STATE MACHINE #
class UserRegistration(StatesGroup):
    # user_choose_event_registration = State()
    user_event_registration_name = State()
    user_event_registration_phone = State()
    user_event_registration_email = State()

    user_event_registration_change_or_confirm = State()

    texts = {
        'UserRegistration:user_event_registration_name': 'Заново введите свое имя: ',
        'UserRegistration:user_event_registration_phone': 'Заново введите свой телефон: ',
        'UserRegistration:user_event_registration_email': 'Заново введите свой email: '
    }


# Start Command #
@user_registration_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! \n/event_registration - Регистрация на мероприятие"
                         f"\n \n",
                         reply_markup=start_registration_keyboard)


# User Select registration #
# StateFilter(None) for check user have not any states #
@user_registration_router.message(or_f(Command("event_registration"), (F.text.lower() == "регистрация на мероприятие")))
@user_registration_router.message(StateFilter(None), Command("event_registration"))
async def user_event_registration(message: Message, state: FSMContext):
    await message.answer("Введите свое имя: ",
                         reply_markup=ReplyKeyboardRemove())

    # WAITING USER NAME #
    await state.set_state(UserRegistration.user_event_registration_name)


# CANCEL #
@user_registration_router.message(StateFilter('*'), F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены")


# BACK #
@user_registration_router.message(StateFilter('*'), F.text.lower() == "изменить предыдущее поле")
@user_registration_router.message(StateFilter('*'), Command("Изменить предыдущее поле"))
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == UserRegistration.user_event_registration_name:
        await message.answer("Предыдущего шага нет, введите свое имя или нажмите 'отмена' ")
        return

    previous_state = None
    for step in UserRegistration.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу\n"
                                 f"{UserRegistration.texts[previous_state.state]}")
            return
        previous_state = step


# GET USER NAME #
@user_registration_router.message(UserRegistration.user_event_registration_name, F.text)
async def user_enter_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text.lower())

    await message.answer("Введите свой номер телефона: ")
    # WAITING USER PHONE #
    await state.set_state(UserRegistration.user_event_registration_phone)


# GET USER PHONE #
@user_registration_router.message(UserRegistration.user_event_registration_phone, F.text)
async def user_enter_name(message: Message, state: FSMContext):
    await state.update_data(user_phone=message.text)

    await message.answer("Введите свой email: ")
    # WAITING USER PHONE #
    await state.set_state(UserRegistration.user_event_registration_email)


# GET USER EMAIL #
@user_registration_router.message(UserRegistration.user_event_registration_email, F.text)
async def user_enter_name(message: Message, state: FSMContext):
    await state.update_data(user_email=message.text)
    data = await state.get_data()

    info = get_user_info(data=data)

    await message.answer("Данные для регистрации: ")
    await message.answer(f"Ваш никнейм - {message.from_user.full_name}\n"
                         f"{info}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Вы готовы зарегистрироваться?",
                         reply_markup=confirm_or_change_user_info_by_user)
    await state.set_state(UserRegistration.user_event_registration_change_or_confirm)


# CONFIRM INFO #
@user_registration_router.message(UserRegistration.user_event_registration_change_or_confirm,
                                  F.text.lower() == "зарегистрироваться")
async def user_confirm(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    info = get_user_info(data=data)

    await orm_user_add_info(session=session, data=data, message=message)

    await message.answer("Зарегистрираван пользователь: ")
    await message.answer(f"Ваш никнейм - {message.from_user.full_name}\n"
                         f"Ваш ID в телеграме - {message.from_user.id}\n"
                         f"{info}", reply_markup=ReplyKeyboardRemove())
    await state.clear()

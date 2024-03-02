# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message


# My Imports #
from keyboards.reply import start_registration_keyboard, confirm_or_change_user_info_by_user

user_registration_router = Router()


# STATE MACHINE #
class UserRegistration(StatesGroup):
    # user_choose_event_registration = State()
    user_event_registration_name = State()
    user_event_registration_phone = State()
    user_event_registration_email = State()

    user_event_registration_change_or_confirm = State()

    user_event_registration_confirm = State()
    user_event_registration_change = State()


# Start Command #
@user_registration_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! \n/event_registration - Регистрация на мероприятие"
                         f"\n \n",
                         reply_markup=start_registration_keyboard)


# User Select registration #
# StateFilter(None) for check user have not any states #
@user_registration_router.message(F.text.lower() == "регистрация на мероприятие")
@user_registration_router.message(StateFilter(None), Command("event_registration"))
async def user_event_registration(message: Message, state: FSMContext):
    await message.answer("Введите свое имя: ",
                         reply_markup=ReplyKeyboardRemove())

    # WAITING USER NAME #
    await state.set_state(UserRegistration.user_event_registration_name)


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

    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    await message.answer("Данные для регистрации: ")
    await message.answer(f"Ваше никнейм - {message.from_user.full_name}\n"
                         f"Ваше имя - {user_name}\n"
                         f"Ваш телефон - {user_phone}\n"
                         f"Ваша почта - {user_email}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Вы готовы зарегистрироваться?",
                         reply_markup=confirm_or_change_user_info_by_user)
    await state.set_state(UserRegistration.user_event_registration_change_or_confirm)


# CHANGE INFO #
@user_registration_router.message(UserRegistration.user_event_registration_change_or_confirm,
                                  F.text.lower() == "изменить информацию")
async def user_change(message: Message, state: FSMContext):
    await state.set_state(UserRegistration.user_event_registration_name)


# CONFIRM INFO #
@user_registration_router.message(UserRegistration.user_event_registration_change_or_confirm,
                                  F.text.lower() == "зарегистрироваться")
async def user_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    await message.answer("Пользователь зарегистрирован ")
    await message.answer(f"Ваше никнейм - {message.from_user.full_name}\n"
                         f"Ваш ID в телеграме - {message.from_user.id}\n"
                         f"Ваше имя - {user_name}\n"
                         f"Ваш телефон - {user_phone}\n"
                         f"Ваша почта - {user_email}", reply_markup=ReplyKeyboardRemove())
    await state.clear()

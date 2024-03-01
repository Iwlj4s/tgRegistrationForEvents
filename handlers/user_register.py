# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter, or_f

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message

# My Imports #
from keyboards.reply import start_registration_keyboard

user_registration_router = Router()


# FSM
class user_registration(StatesGroup):
    # user_choose_event_registration = State()
    user_event_registration_name = State()
    user_event_registration_phone = State()
    user_event_registration_email = State()


# Start Command #
@user_registration_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! \n/event_registration - Регистрация на мероприятие"
                         f"\n \n",
                         reply_markup=start_registration_keyboard)


# User Select registration #
@user_registration_router.message(F.text.lower() == "регистрация на мероприятие")
@user_registration_router.message(StateFilter(None), Command("event_registration"))
async def user_event_registration(message: Message, state: FSMContext):
    await message.answer("Введите свое имя: ")

    # Waiting USER NAME #
    await state.set_state(user_registration.user_event_registration_name)


# Get USER NAME #
@user_registration_router.message(user_registration.user_event_registration_name)
async def user_enter_name(message: Message, state: FSMContext):

    await state.update_data(user_name=message.text.lower())

    data = await state.get_data()
    user_name = data.get("user_name")

    await message.answer(f"Ваш никнейм - {message.from_user.first_name}, Ваше Имя - {user_name}")


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
from keyboards.reply import start_registration_keyboard, confirm_or_change_user_info_by_user, get_keyboard

from user_data.get_user_info import get_user_info

from database.orm_query import orm_user_add_info, orm_get_events, orm_get_user_by_tg_id

from checks.check_user_input import user_id_already_in_db, user_input_id_event_is_correct

user_registration_router = Router()


# STATE MACHINE #


class UserRegistration(StatesGroup):
    # user_choose_event_registration = State()
    user_event_registration_event = State()
    user_event_registration_name = State()
    user_event_registration_phone = State()
    user_event_registration_email = State()

    user_event_registration_change_or_confirm = State()

    texts = {
        'UserRegistration:user_event_registration_event': 'Заново введите id мероприятия ',
        'UserRegistration:user_event_registration_name': 'Заново введите свое имя: ',
        'UserRegistration:user_event_registration_phone': 'Заново введите свой телефон: ',
        'UserRegistration:user_event_registration_email': 'Заново введите свой email: '
    }


# Start Command #
@user_registration_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! \n/event_registration - Регистрация на мероприятие"
                         f"\n/events - список мероприятий",
                         reply_markup=start_registration_keyboard)


# EVENTS list #
@user_registration_router.message(or_f(Command("event"), (F.text.lower() == "список мероприятий")))
async def events_list(message: Message, session: AsyncSession):
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"User event_id - {event.id}\n"
                             f"Дата мероприятия - {event.event_date}\n"
                             f"Начало мероприятия - {event.event_time}\n")


# User Select registration #
# StateFilter(None) for check user have not any states #
@user_registration_router.message(or_f(Command("event_registration"), (F.text.lower() == "регистрация на мероприятие")))
@user_registration_router.message(StateFilter(None), Command("event_registration"))
async def user_event_registration(message: Message, state: FSMContext, session: AsyncSession):
    # Check if user already in the database
    if user_id_already_in_db(session=session, tg_id=message.from_user.id):
        user = await orm_get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        if user:
            await message.answer(f"Вы уже зарегистрированы на мероприятие - {user.event}",
                                 reply_markup=start_registration_keyboard)
            print(f"Пользователь {message.from_user.id} {message.from_user.full_name} пытается повторно "
                  f"зарегистрироваться")
            return

    await message.answer("Введите id мероприятия, на которое нужно зарегистрироваться: ",
                         reply_markup=ReplyKeyboardRemove())
    # WAITING EVENT ID #
    await state.set_state(UserRegistration.user_event_registration_event)


# CANCEL #
@user_registration_router.message(StateFilter('*'), F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Все действия отменены", reply_markup=start_registration_keyboard)


# BACK #
@user_registration_router.message(StateFilter('*'), F.text.lower() == "изменить предыдущее поле")
@user_registration_router.message(StateFilter('*'), Command("Изменить предыдущее поле"))
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == UserRegistration.user_event_registration_event:
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


# GET USER EVENT #
@user_registration_router.message(UserRegistration.user_event_registration_event, F.text)
async def user_enter_event(message: Message, state: FSMContext, session: AsyncSession):
    if not await user_input_id_event_is_correct(session=session, event_id=message.text):
        await message.answer("введите корректный id мероприятия\n"
                             "/event - мероприятия", reply_markup=start_registration_keyboard)
        return

    await state.update_data(event_id=message.text)

    await message.answer("Введите свое имя: ",
                         reply_markup=get_keyboard(
                             "изменить предыдущее поле",
                             "отмена"
                         ))

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

    info = get_user_info(data=data)

    await message.answer("Данные для регистрации: ")
    await message.answer(f"Ваш ID в телеграме - {message.from_user.id}"
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
    await message.answer(f"Ваш ID в телеграме - {message.from_user.id}\n"
                         f"{info}", reply_markup=ReplyKeyboardRemove())
    await state.clear()


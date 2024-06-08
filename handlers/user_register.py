# Aiogram Imports #
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# SqlAlchemy Imports #
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# My Imports #
from keyboards.reply import (start_registration_keyboard, confirm_or_change_user_info_by_user, get_keyboard,
                             after_registration_user_keyboard, cancel_or_back_user)
from keyboards.inline import get_callback_btns

from user_data.get_user_info import get_user_info

from checks.check_user_input import (user_id_already_in_db, user_input_id_event_is_correct, user_try_one_more,
                                     user_in_users_events, user_in_users_events_for_unsubscribe, validate_phone_input,
                                     validate_email_input)

from database.models import Events
from database.orm_query import orm_user_add_info, orm_get_events, orm_get_user_by_tg_id, orm_save_user_event_info, \
    orm_get_user_subscribed_events, orm_get_events_id, orm_unsubscribe_from_event

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
    await message.answer(f"Привет, {message.from_user.first_name}! \n/registration - Регистрация\n"
                         f"/event_registration - Регистрация на мероприятие"
                         f"\n/events - список мероприятий",
                         reply_markup=start_registration_keyboard)


# EVENTS list #
@user_registration_router.message(or_f(Command("event"), (F.text.lower() == "список мероприятий")))
async def events_list_user(message: Message, session: AsyncSession):
    events_message = "Список мероприятий:\n"
    user_id = message.from_user.id
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        user_subscribed = await user_in_users_events_for_unsubscribe(session=session,
                                                                     user_tg_id=user_id, user_event_id=event.id)

        event_info = f"Id мероприятия - {event.id}\n" \
                     f"Дата мероприятия - {event.event_date}\n" \
                     f"Начало мероприятия - {event.event_time}\n"

        if user_subscribed:
            event_info = f"Вы записаны на - {event.event_name}\n" + event_info

        else:
            event_info = f"{event.event_name}\n" + event_info

        await message.answer(event_info)


# USER REGISTRATION #
# StateFilter(None) for check user have not any states #
@user_registration_router.message(or_f(Command("registration"), (F.text.lower() == "регистрация")))
@user_registration_router.message(StateFilter(None), Command("registration"))
async def user_registration(message: Message, state: FSMContext, session: AsyncSession):
    # Check if user already in the database
    if user_id_already_in_db(session=session, tg_id=message.from_user.id):
        user = await orm_get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        if user:
            await message.answer(f"Вы уже зарегистрированы",
                                 reply_markup=after_registration_user_keyboard)
            return

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
    await message.answer("Все действия отменены", reply_markup=after_registration_user_keyboard)


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

    await message.answer("Введите свой номер телефона ('+7(XXX)XXX-XX-XX'): ",
                         reply_markup=cancel_or_back_user)
    # WAITING USER PHONE #
    await state.set_state(UserRegistration.user_event_registration_phone)


# GET USER PHONE #
@user_registration_router.message(UserRegistration.user_event_registration_phone, F.text)
async def user_enter_name(message: Message, state: FSMContext):
    if not await validate_phone_input(message.text):
        await message.answer(
            "Некорректный формат номера телефона.\nПожалуйста, введите номер в формате +7(XXX)XXX-XX-XX.")
        return

    await state.update_data(user_phone=str(message.text))

    await message.answer("Введите свой email: ")

    # WAITING USER PHONE #
    await state.set_state(UserRegistration.user_event_registration_email)


# GET USER EMAIL #
@user_registration_router.message(UserRegistration.user_event_registration_email, F.text)
async def user_enter_name(message: Message, state: FSMContext):
    user_email = await validate_email_input(message.text)
    if user_email is None:
        await message.answer("Некорректный формат почты.\nПожалуйста, введите почту в формате 'abcd123@gmail.com':")
        return

    await state.update_data(user_email=user_email)

    data = await state.get_data()

    info = get_user_info(data=data)

    await message.answer("Данные для регистрации: ")
    await message.answer(f"Ваш ID в телеграме - {message.from_user.id}\n"
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

    await message.answer("Зарегистрирован пользователь: ")
    await message.answer(f"Ваш ID в телеграме - {message.from_user.id}\n"
                         f"{info}",
                         reply_markup=after_registration_user_keyboard)
    await state.clear()


# Check user
@user_registration_router.message(F.text.lower() == "посмотреть пользователя")
async def look_user(message: Message, state: FSMContext, session: AsyncSession):
    user_tg_id = message.from_user.id
    user_info = await orm_get_user_by_tg_id(session=session, tg_id=int(user_tg_id))

    await message.answer(f"Зарегистрированный пользователь - {user_info.tg_id}\n"
                         f"Id пользователя - {user_info.id}\n"
                         f"Телеграмм Id - {user_info.tg_id}\n"
                         f"Имя - {user_info.name}\n"
                         f"Телефон - {user_info.phone}\n"
                         f"Эл. Почта - {user_info.email}\n", reply_markup=after_registration_user_keyboard)


# REGISTRATION ON EVENT #
@user_registration_router.message(or_f(Command("event_registration"), (F.text.lower() == "регистрация на мероприятие")))
@user_registration_router.message(StateFilter(None), Command("event_registration"))
async def user_event_registration(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Вы в 'стадии' регистрации на мероприятие", reply_markup=after_registration_user_keyboard)
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"Адрес мероприятия - {event.event_address}\n"
                             f"User event_id - {event.id}\n"
                             f"Дата мероприятия - {event.event_date}\n"
                             f"Начало мероприятия - {event.event_time}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Записаться': f'event_registration_{event.id}'
                             })
                             )


# Add user in event
@user_registration_router.callback_query(F.data.startswith("event_registration_"))
async def process_event_registration(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = int(callback_query.data.split('_')[-1])
    data = await state.get_data()

    events = select(Events.event_name).where(Events.id == event_id)
    result = await session.execute(events)
    event_name = result.scalar()

    check_user = await user_try_one_more(session=session, tg_id=callback_query.from_user.id, event_id=event_id)

    if check_user:
        await callback_query.answer("")
        await callback_query.message.answer(f"Вы уже записаны на мероприятие {event_name}")
        return

    # Save user event registration info to UsersEvents table
    await orm_save_user_event_info(session=session, tg_id=callback_query.from_user.id, event_id=event_id)

    await callback_query.answer("Вы успешно записаны на мероприятие!")
    await callback_query.message.answer(f"Вы успешно записаны на мероприятие {event_name}")


# UNSUBSCRIBE from UsersEvents
@user_registration_router.message(F.text.lower() == "отписаться от мероприятия")
async def unsubscribe_from_event(message: Message, session: AsyncSession):
    check_user = await user_in_users_events(session=session, user_tg_id=message.from_user.id)

    if not check_user:
        await message.answer("Вы не записаны на мероприятия")
        return

    await message.answer("Список ваших мероприятий:")
    for event in await orm_get_user_subscribed_events(session=session, user_id=message.from_user.id):
        event_by_id = await orm_get_events_id(session=session, event_id=event.user_event_id)

        if event_by_id is None:
            await message.answer("Ошибка: Информация о мероприятии не найдена.")
            continue

        await message.answer(f"{event.user_event_name}\n"
                             f"Адрес мероприятия - {event.user_event_address}\n"
                             f"Id мероприятия - {event.user_event_id}\n"
                             f"Дата мероприятия - {event_by_id.event_date}\n"
                             f"Начало мероприятия - {event_by_id.event_time}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Отписаться от мероприятия': f'unsubscribe_from_event_{event.user_event_id}'
                             })
                             )


@user_registration_router.callback_query(F.data.startswith("unsubscribe_from_event_"))
async def unsubscribe_from_event_(callback_query: CallbackQuery, session: AsyncSession):
    event_id = int(callback_query.data.split('_')[-1])
    user_id = callback_query.from_user.id

    # Get the event name before unsubscribing
    event = await orm_get_events_id(session=session, event_id=event_id)
    event_name = event.event_name

    check_user = await user_in_users_events_for_unsubscribe(session=session,
                                                            user_tg_id=callback_query.from_user.id,
                                                            user_event_id=event_id)

    if not check_user:
        await callback_query.message.answer(f"Вы не записаны на мероприятие {event_name}")
        return

    await orm_unsubscribe_from_event(session=session, event_id=event_id, user_id=user_id)

    await callback_query.answer("Вы отписались от мероприятия!")
    await callback_query.message.answer(f"Вы отписались от мероприятия! {event_name}")

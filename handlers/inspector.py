# Aiogram Imports #
from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

# SqlAlchemy Imports #
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# My Imports #

from database.models import Inspectors
from database.orm_query import orm_get_user_by_tg_id, orm_get_event_by_event_name, orm_confirm_user, \
    orm_get_user_on_event_usr_event_id, orm_get_events, orm_get_attendance

from checks.check_user_input import user_id_already_in_db, user_in_users_events, user_in_users_events_for_inspector, \
    user_already_on_event

from keyboards.reply import start_inspector_keyboard, after_registration_user_keyboard, start_registration_keyboard, \
    cancel_or_back_for_check_user, confirm_user_by_inspector, cancel_or_back_or_skip_for_check_user

from other_functions.get_code_for_inspector import get_code
from user_data.get_user_info_from_inspector import get_user_info_from_inspector

inspector_router = Router()


class UserCheck(StatesGroup):
    enter_user_tg_id = State()
    enter_event_name = State()
    check_sent_code = State()
    inspector_add_notes = State()

    inspector_confirm_user = State()

    texts = {
        'UserCheck:enter_user_tg_id': 'Заново введите телеграм id пользователя: ',
        'UserCheck:enter_event_name': 'Заново введите имя мероприятия: ',
        'UserCheck:check_sent_code': 'Заново введите проверочный код пользователя: ',
        'UserCheck:inspector_add_notes': 'Заново заметки: '
    }


# Start For Inspector#
@inspector_router.message(Command("inspector"))
async def inspector_login(message: Message, session: AsyncSession, bot):
    db_inspector = select(Inspectors.tg_id)
    inspectors = await session.execute(db_inspector)

    inspector_ids = [inspector[0] for inspector in inspectors]

    if message.from_user.id not in inspector_ids:
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        await bot.send_message(message.from_user.id, "Вы зашли как проверяющий",
                               reply_markup=start_inspector_keyboard)


# Quit from Inspector #
@inspector_router.message(F.text.lower() == "выйти из проверяющего")
async def exit_from_inspector(message: Message, session: AsyncSession):
    if user_id_already_in_db(session=session, tg_id=message.from_user.id):
        user = await orm_get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        if user:
            await message.answer("Вы вышли из роли проверяющего",
                                 reply_markup=after_registration_user_keyboard)
    else:
        await message.answer("Вы вышли из роли проверяющего",
                             reply_markup=start_registration_keyboard)


# Events list
@inspector_router.message(or_f(Command("event"), (F.text.lower() == "мероприятия")))
async def events_list_inspector(message: Message, session: AsyncSession):
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"Адрес мероприятия - {event.event_address}\n"
                             f"Id мероприятия - {event.id}\n"
                             f"Дата мероприятия - {event.event_date}\n"
                             f"Начало мероприятия - {event.event_time}\n")


# Check Attendance
@inspector_router.message(F.text.lower() == "просмотр посещений мероприятий")
async def attendance_list_inspector(message: Message, session: AsyncSession):
    await message.answer("Список посещений:")
    for attendance in await orm_get_attendance(session=session):
        await message.answer(f"Телеграм id пользователя - {attendance.user_tg_id}\n"
                             f"Id мероприятия - {attendance.user_event_id}\n"
                             f"Название мероприятия - {attendance.user_event_name}\n"
                             f"Id проверяющего - {attendance.inspector_id}\n"
                             f"Заметки проверяющего - {attendance.inspector_notes}\n")


# CANCEL #
@inspector_router.message(StateFilter('*'), F.text.lower() == "[inspector-check] отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Все действия отменены", reply_markup=start_inspector_keyboard)


# BACK FOR INSPECTOR #
@inspector_router.message(StateFilter('*'), F.text.lower() == "[inspector-check] изменить предыдущее поле")
async def inspector_back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == UserCheck.enter_user_tg_id:
        await message.answer("Вы находитесь на первом шаге. \n"
                             "Заново введите телеграм id пользователя или нажмите 'отмена'")
        return

    previous_state = None
    for step in UserCheck.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу:\n{UserCheck.texts[previous_state.state]}")
            return
        previous_state = step


# Start User Check
@inspector_router.message(StateFilter(None), F.text.lower() == "начать проверку пользователя")
async def start_user_check(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Введите телеграм id пользователя: ",
                         reply_markup=cancel_or_back_for_check_user)

    # WAIT USER ID
    await state.set_state(UserCheck.enter_user_tg_id)


# Check user in UsersEvents by id
@inspector_router.message(UserCheck.enter_user_tg_id, F.text)
async def enter_user_tg_id(message: Message, state: FSMContext, session: AsyncSession):
    user_tg_id = message.text
    user_in_db = await user_in_users_events(session=session, user_tg_id=user_tg_id)

    if not user_in_db:
        await message.answer("Пользователя нет в базе данных")
        return

    else:
        user = await orm_get_user_by_tg_id(session=session, tg_id=int(user_tg_id))
        user_name = user.name
        await state.update_data(user_name=user_name)
        await state.update_data(user_tg_id=user_tg_id)
        await message.answer(f"Имя пользователя - {user_name}")
        await message.answer("Введите название мероприятия: ")

        # WAIT EVENT NAME
        await state.set_state(UserCheck.enter_event_name)


# Check user subscribed on event
@inspector_router.message(UserCheck.enter_event_name, F.text)
async def enter_event_name(message: Message, state: FSMContext, session: AsyncSession, bot):
    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    user_event_name = message.text.title()

    event = await orm_get_event_by_event_name(session=session, event_name=str(user_event_name))

    user_in_user_event = await user_in_users_events_for_inspector(session=session, user_tg_id=user_tg_id,
                                                                  user_event_name=user_event_name)

    if not user_in_user_event:
        await message.answer("Пользователь не зарегистрирован на это мероприятие или "
                             "мероприятие закрыто / не существует / удалено")
        return

    else:
        if await user_already_on_event(session=session, user_tg_id=user_tg_id, user_event_id=event.user_event_id):
            await message.answer(f"У данного пользователя {user_tg_id} уже подтверждена запись на это мероприятие "
                                 f"{user_event_name}")
            return

        else:
            inspector_code = get_code()
            user_event_id = event.user_event_id
            await state.update_data(user_event_name=message.text.title())
            await state.update_data(inspector_code=inspector_code)
            await state.update_data(user_event_id=user_event_id)

            await bot.send_message(user_tg_id, f"Код для подтверждения посещения мероприятия - {inspector_code}\n"
                                               f"Сообщите его ТОЛЬКО проверяющему на мероприятии")
            await message.answer(f"Пользователю отправлен код\n"
                                 f"Введите его для подтверждения личности пользователя: ")

            # WAIT CODE
            await state.set_state(UserCheck.check_sent_code)


# Check sent code
@inspector_router.message(UserCheck.check_sent_code, F.text)
async def check_sent_code(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    user_event_name = data.get("user_event_name")
    inspector_code = data.get("inspector_code")

    if not inspector_code == message.text:
        await message.answer("Код неверный")
        return

    else:
        await message.answer("Код совпадает!")
        await message.answer("Добавьте заметки:",
                             reply_markup=cancel_or_back_or_skip_for_check_user)

        # WAIT NOTES
        await state.set_state(UserCheck.inspector_add_notes)


# Inspector add / skip notes
@inspector_router.message(UserCheck.inspector_add_notes, F.text)
async def add_notes(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(inspector_id=int(message.from_user.id))

    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    user_event_name = data.get("user_event_name")

    if message.text == "[Inspector-check] Пропустить поле":
        inspector_notes = "Заметок нет"
        await state.update_data(inspector_notes=inspector_notes)

    else:
        await state.update_data(inspector_notes=message.text.title())

    await message.answer(f"Вы подтверждаете, что пользователь {user_tg_id} "
                         f"будет присутствовать на мероприятии {user_event_name}?",
                         reply_markup=confirm_user_by_inspector)

    # WAIT CONFIRM
    await state.set_state(UserCheck.inspector_confirm_user)


# Confirm user
@inspector_router.message(UserCheck.inspector_confirm_user, F.text.lower() == "подтвердить присутствие пользователя")
async def confirm_user(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    user_event_name = data.get("user_event_name")
    inspector_code = data.get("inspector_code")

    event = await orm_get_event_by_event_name(session=session, event_name=str(user_event_name))
    user_event_id = event.user_event_id

    await orm_confirm_user(session=session, data=data)
    await message.answer("Пользователь подтвержден!",
                         reply_markup=start_inspector_keyboard)

    await state.clear()


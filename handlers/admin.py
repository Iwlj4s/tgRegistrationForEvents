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
from keyboards.reply import (start_registration_keyboard, start_admin_keyboard,
                             confirm_or_change_user_info_by_admin, confirm_or_change_event_info_by_admin,
                             cancel_or_back_for_user_change_admin,
                             cancel_or_back_for_add_event_admin)
from keyboards.inline import get_callback_btns

from user_data.get_user_info import get_user_info, get_user_data_for_admin
from user_data.get_event_info import get_event_info


from database.models import Admins
from database.orm_query import orm_get_users, orm_delete_user, orm_get_events, orm_get_user, orm_update_user, \
    orm_delete_user_from_events, orm_update_users_events, orm_add_event, orm_delete_event, \
    orm_delete_event_from_users_events, orm_get_events_id, orm_update_users_events_by_event_id, orm_update_event, \
    orm_add_info_in_closed_events

admin_router = Router()


class ChangeUserInfo(StatesGroup):
    change_user_event_registration_name = State()
    change_user_event_registration_phone = State()
    change_user_event_registration_email = State()

    changing_user_event_registration_change_or_confirm = State()

    user_for_change = None

    texts = {
        'ChangeUserInfo:change_user_event_registration_name': 'Измените имя пользователя: ',
        'ChangeUserInfo:change_user_event_registration_phone': 'Измените телефон пользователя: ',
        'ChangeUserInfo:change_user_event_registration_email': 'Измените email пользователя: '
    }


class AddEvent(StatesGroup):
    add_event_name = State()
    add_event_date = State()
    add_event_time = State()

    confirm_or_change_event = State()

    event_for_change = None

    texts = {
        'AddEvent:add_event_name': 'Измените имя мероприятия',
        'AddEvent:add_event_date': 'Измените дату мероприятия',
        'AddEvent:add_event_time': 'Измените время мероприятия'
    }


# Start For admin #
@admin_router.message(Command("admin"))
async def admin_login(message: Message, session: AsyncSession):
    db_adm = select(Admins.tg_id)
    admins_db = await session.execute(db_adm)

    admin_ids = [admin[0] for admin in admins_db]  # Extract Telegram IDs from the result set

    print(f"Admin_db: {admin_ids}")
    print(f"Msg from user: {message.from_user.id}")

    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав", reply_markup=start_registration_keyboard)
    else:
        await message.answer("Вы зашли как администратор", reply_markup=start_admin_keyboard)


# Quit from admin #
@admin_router.message(F.text.lower() == "выйти из администратора")
async def exit_from_admin(message: Message):
    await message.answer("Вы вышли из роли администратора",
                         reply_markup=start_registration_keyboard)


# USER STUFF #
# Check Users
@admin_router.message(F.text.lower() == "просмотр пользователей")
async def get_users(message: Message, session: AsyncSession):
    await message.answer("Вот список пользователей: ")
    for user in await orm_get_users(session=session):
        await message.answer(f"User id - {user.id}\n"
                             f"User tg_id - {user.tg_id}\n"
                             f"User Name - {user.name}\n"
                             f"User Phone - {user.phone}\n"
                             f"User Email - {user.email}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_user_{user.id}',
                                 'Удалить': f'delete_user_{user.tg_id}'
                             })
                             )


# Delete User
@admin_router.callback_query(F.data.startswith('delete_user_'))
async def delete_user(callback: CallbackQuery, session: AsyncSession):
    print("Delete function start !")
    user_id = callback.data.split("_")[-1]
    await orm_delete_user(session=session, user_id=int(user_id))
    await orm_delete_user_from_events(session=session, user_id=int(user_id))

    await callback.answer("Пользователь удален")
    await callback.message.answer("Пользователь удален!")


# Change user
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_user_'))
async def change_user(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.data.split("_")[-1]
    user_for_change = await orm_get_user(session=session, user_id=int(user_id))

    ChangeUserInfo.user_for_change = user_for_change

    await callback.answer()
    await callback.message.answer("Измените имя пользователя: ",
                                  reply_markup=ReplyKeyboardRemove())

    # WAITING USER NAME #
    await state.set_state(ChangeUserInfo.change_user_event_registration_name)


# CANCEL #
@admin_router.message(StateFilter('*'), F.text.lower() == "отмена")
@admin_router.message(StateFilter('*'), Command("Отмена"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    if ChangeUserInfo.user_for_change:
        ChangeUserInfo.user_for_change = None

    await state.clear()
    await message.answer("Все действия отменены", reply_markup=start_admin_keyboard)


# BACK FOR USER #
@admin_router.message(StateFilter('*'), F.text.lower() == "[admin-user] изменить предыдущее поле")
async def admin_back_user_info_handler(message: Message, state: FSMContext):
    print("XUi")
    current_state = await state.get_state()

    if current_state == ChangeUserInfo.change_user_event_registration_name:
        await message.answer("Вы находитесь на первом шаге изменения информации пользователя. \n"
                             "Введите новое имя пользователя или нажмите 'отмена'")
        return

    previous_state = None
    for step in ChangeUserInfo.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу:\n{ChangeUserInfo.texts[previous_state.state]}")
            return
        previous_state = step


# BACK FOR EVENT #
@admin_router.message(StateFilter('*'), F.text.lower() == "[admin-event] изменить предыдущее поле")
async def admin_back_event_add_handler(message: Message, state: FSMContext):
    print("Back Pressed!")
    current_state = await state.get_state()

    if current_state == AddEvent.add_event_name:
        await message.answer("Предыдущего шага нет\n"
                             "Введите название мероприятия или нажмите 'отмена' ")
        return

    previous_state = None
    for step in AddEvent.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу\n"
                                 f"{AddEvent.texts[previous_state.state]}")
            return
        previous_state = step


# GET USER NAME
@admin_router.message(ChangeUserInfo.change_user_event_registration_name, F.text)
async def admin_enter_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text.lower())

    await message.answer("Измените номер телефона пользователя: ",
                         reply_markup=cancel_or_back_for_user_change_admin)
    # WAITING USER PHONE #
    await state.set_state(ChangeUserInfo.change_user_event_registration_phone)


# GET USER PHONE
@admin_router.message(ChangeUserInfo.change_user_event_registration_phone, F.text)
async def admin_enter_phone(message: Message, state: FSMContext):
    await state.update_data(user_phone=message.text)

    await message.answer("Измените email пользователя: ")
    # WAITING USER EMAIL #
    await state.set_state(ChangeUserInfo.change_user_event_registration_email)


# GET USER EMAIL
@admin_router.message(ChangeUserInfo.change_user_event_registration_email, F.text)
async def admin_enter_email(message: Message, state: FSMContext):
    await state.update_data(user_email=message.text)
    data = await state.get_data()

    info = get_user_info(data=data)

    await message.answer("Данные для изменения информации: ")
    await message.answer(f"{info}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Изменить информацию?",
                         reply_markup=confirm_or_change_user_info_by_admin)
    await state.set_state(ChangeUserInfo.changing_user_event_registration_change_or_confirm)


# CONFIRM USER INFO
@admin_router.message(ChangeUserInfo.changing_user_event_registration_change_or_confirm,
                      F.text.lower() == "изменить информацию")
async def admin_confirm(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    info = get_user_data_for_admin(data=data)
    print(info)
    print(data)

    await orm_update_user(session=session, user_id=ChangeUserInfo.user_for_change.id, data=data, message=message)
    await orm_update_users_events(session=session, user_tg_id=ChangeUserInfo.user_for_change.tg_id, data=data)

    await message.answer("Пользователь изменен: ")
    await message.answer(f"{info}", reply_markup=start_admin_keyboard)

    await state.clear()
    ChangeUserInfo.user_for_change = None


# EVENT STUFF #
# Check Events
@admin_router.message(or_f(Command("event"), (F.text.lower() == "просмотр мероприятий")))
async def events_list(message: Message, session: AsyncSession):
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"User event_id - {event.id}\n"
                             f"Дата мероприятия - {event.event_date}\n"
                             f"Начало мероприятия - {event.event_time}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_event_{event.id}',
                                 'Закрыть': f'close_event_{event.id}',
                                 'Удалить': f'delete_event_{event.id}'
                             })
                             )


# Add Event
@admin_router.message(StateFilter(None), F.text.lower() == "добавить мероприятие")
async def add_event(message: Message, state: FSMContext):
    await message.answer("Введите название мероприятия: ",
                         reply_markup=cancel_or_back_for_add_event_admin)

    # WAIT EVENT NAME #
    await state.set_state(AddEvent.add_event_name)


# Close Event
@admin_router.callback_query(F.data.startswith('close_event_'))
async def close_event(callback: CallbackQuery, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    event = await orm_get_events_id(session=session, event_id=int(event_id))

    await orm_add_info_in_closed_events(session=session, event=event)   # Add closing event in closedEvents
    await orm_delete_event(session=session, event_id=int(event_id))     # Delete closing event from Events
    await orm_delete_event_from_users_events(session=session, event_id=int(event_id))   # Delete closing event from
    # usersEvents

    await callback.answer("Мероприятие закрыто!")
    await callback.message.answer("Мероприятие закрыто!")


# Delete Event
@admin_router.callback_query(F.data.startswith('delete_event_'))
async def delete_event(callback: CallbackQuery, session: AsyncSession):
    print("Event Delete function start !")
    event_id = callback.data.split("_")[-1]
    await orm_delete_event(session=session, event_id=int(event_id))  # Delete closing event from Events
    await orm_delete_event_from_users_events(session=session, event_id=int(event_id))   # Delete closing event from
    # usersEvents

    await callback.answer("Мероприятие удалено!")
    await callback.message.answer("Мероприятие удалено!")


# Change event
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_event_'))
async def change_event(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]

    event_for_change = await orm_get_events_id(session=session, event_id=int(event_id))

    AddEvent.event_for_change = event_for_change

    await callback.answer()
    await callback.message.answer("Измените название меропрития: ",
                                  reply_markup=cancel_or_back_for_add_event_admin)

    # WAITING USER NAME #
    await state.set_state(AddEvent.add_event_name)


# Event Name
@admin_router.message(AddEvent.add_event_name, F.text)
async def add_event_name(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text.title())

    await message.answer("Введите дату мероприятия: ")

    # WAITING EVENT DATE #
    await state.set_state(AddEvent.add_event_date)


# Event Date
@admin_router.message(AddEvent.add_event_date, F.text)
async def add_event_date(message: Message, state: FSMContext):
    await state.update_data(event_date=message.text)

    await message.answer("Введите время мероприятия: ")

    # WAITING EVENT DATE #
    await state.set_state(AddEvent.add_event_time)


# Event Time
@admin_router.message(AddEvent.add_event_time, F.text)
async def add_event_time(message: Message, state: FSMContext):
    await state.update_data(event_time=message.text)

    data = await state.get_data()
    info = get_event_info(data=data)

    await message.answer("Мероприятие: \n"
                         f"{info}")

    # WAITING CONFIRM / CHANGE EVENT #
    await message.answer("Добавить мероприятие?",
                         reply_markup=confirm_or_change_event_info_by_admin)
    await state.set_state(AddEvent.confirm_or_change_event)


# Adding Event
@admin_router.message(AddEvent.confirm_or_change_event, F.text.lower() == "добавить мероприятие")
async def add_event_time(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    info = get_event_info(data=data)

    if AddEvent.event_for_change:
        await orm_update_event(session=session, event_id=AddEvent.event_for_change.id, data=data)   # Update Events
        # Update usersEvents
        await orm_update_users_events_by_event_id(session=session, event_id=AddEvent.event_for_change.id, data=data)

        await message.answer(f"Вы изменили мероприятие - {AddEvent.event_for_change.event_name}\n"
                             f"{info}",
                             reply_markup=start_admin_keyboard)

    else:
        await orm_add_event(session=session, data=data, message=message)

        await message.answer("Вы добавили мероприятие: \n"
                             f"{info}",
                             reply_markup=start_admin_keyboard)

    await state.clear()
    AddEvent.event_for_change = None


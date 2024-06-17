# Aiogram Imports #
import datetime

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
# from app import bot, dp
from checks.check_user_input import user_id_already_in_db, validate_date_input, validate_time_input, \
    validate_email_input, validate_phone_input, validate_tg_id_input, no_same_event, validate_address_input

from keyboards.reply import (start_registration_keyboard, start_admin_keyboard,
                             confirm_or_change_user_info_by_admin, confirm_or_change_event_info_by_admin,
                             cancel_or_back_for_user_change_admin,
                             cancel_or_back_for_add_event_admin, after_registration_user_keyboard,
                             cancel_or_back_for_admin_admin, confirm_or_change_admin_info_by_admin,
                             cancel_or_back_for_admin_change_admin, cancel_or_back_for_admin_change_inspector,
                             cancel_or_back_for_admin_inspector, confirm_or_change_inspector_info_by_admin,
                             cancel_or_back_or_skip_for_add_event_admin)
from keyboards.inline import get_callback_btns

from user_data.get_user_info import get_user_info, get_user_data_for_admin, get_admin_info, get_inspector_info
from user_data.get_event_info import get_event_info

from database.models import Admins
from database.orm_query import orm_get_users, orm_delete_user, orm_get_events, orm_get_user, orm_update_user, \
    orm_delete_user_from_events, orm_update_users_events, orm_add_event, orm_delete_event, \
    orm_delete_event_from_users_events, orm_get_events_id, orm_update_users_events_by_event_id, orm_update_event, \
    orm_add_info_in_closed_events, orm_get_user_by_tg_id, orm_get_users_from_users_events, orm_admin_add_info, \
    orm_get_admins, orm_delete_admin, orm_get_admin, orm_update_admin, orm_get_attendance, orm_get_inspectors, \
    orm_delete_inspector, orm_get_inspector, orm_update_inspector, orm_inspector_add_info

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
    add_event_address = State()
    add_event_date = State()
    add_event_time = State()

    confirm_or_change_event = State()

    event_for_change = None

    texts = {
        'AddEvent:add_event_name': 'Измените имя мероприятия',
        'AddEvent:add_event_address': 'Измените адрес мероприятия',
        'AddEvent:add_event_date': 'Измените дату мероприятия',
        'AddEvent:add_event_time': 'Измените время мероприятия'
    }


class AddAdmin(StatesGroup):
    add_admin_tg_id = State()
    add_admin_name = State()
    add_admin_phone = State()
    add_admin_email = State()

    confirm_or_change_admin = State()

    admin_for_change = None

    texts = {
        'AddAdmin:add_admin_tg_id': 'Измените телеграм id администратора',
        'AddAdmin:add_admin_name': 'Измените имя администратора',
        'AddAdmin:add_admin_phone': 'Измените телефон администратора',
        'AddAdmin:add_admin_email': 'Измените эл.почту администратора'
    }


class AddInspector(StatesGroup):
    add_inspector_tg_id = State()
    add_inspector_name = State()
    add_inspector_phone = State()
    add_inspector_email = State()

    confirm_or_change_inspector = State()

    inspector_for_change = None

    texts = {
        'AddInspector:add_inspector_tg_id': 'Измените телеграм id проверяющего',
        'AddInspector:add_inspector_name': 'Измените имя проверяющего',
        'AddInspector:add_inspector_phone': 'Измените телефон проверяющего',
        'AddInspector:add_inspector_email': 'Измените эл.почту проверяющего'
    }


# Start For admin #
@admin_router.message(Command("admin"))
async def admin_login(message: Message, session: AsyncSession, bot):
    db_adm = select(Admins.tg_id)
    admins_db = await session.execute(db_adm)

    admin_ids = [admin[0] for admin in admins_db]  # Extract Telegram IDs from the result set

    if message.from_user.id not in admin_ids:
        await bot.send_message(message.from_user.id, "У вас нет прав", reply_markup=start_registration_keyboard)
        # await message.answer("У вас нет прав", reply_markup=start_registration_keyboard)
    else:
        # await message.answer("Вы зашли как администратор", reply_markup=start_admin_keyboard)
        await bot.send_message(message.from_user.id, "Вы зашли как администратор", reply_markup=start_admin_keyboard)


# Quit from admin #
@admin_router.message(F.text.lower() == "выйти из администратора")
async def exit_from_admin(message: Message, session: AsyncSession):
    if user_id_already_in_db(session=session, tg_id=message.from_user.id):
        user = await orm_get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        if user:
            await message.answer("Вы вышли из роли администратора",
                                 reply_markup=after_registration_user_keyboard)
    else:
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
                                  reply_markup=cancel_or_back_for_user_change_admin)

    # WAITING USER NAME #
    await state.set_state(ChangeUserInfo.change_user_event_registration_name)


# CANCEL #
@admin_router.message(StateFilter('*'), F.text.lower() == "[admin] отмена")
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


# BACK FOR ADMIN #
@admin_router.message(StateFilter('*'), F.text.lower() == "[admin-admin] изменить предыдущее поле")
async def admin_back_admin_info_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AddAdmin.add_admin_tg_id:
        await message.answer("Вы находитесь на первом шаге изменения информации администратора. \n"
                             "Введите телеграм id администратора или нажмите 'отмена'")
        return

    previous_state = None
    for step in AddAdmin.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу:\n{AddAdmin.texts[previous_state.state]}")
            return
        previous_state = step


# BACK FOR INSPECTOR #
@admin_router.message(StateFilter('*'), F.text.lower() == "[admin-inspector] изменить предыдущее поле")
async def admin_back_inspector_info_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AddInspector.add_inspector_tg_id:
        await message.answer("Вы находитесь на первом шаге изменения информации проверяющего. \n"
                             "Введите телеграм id проверяющего или нажмите 'отмена'")
        return

    previous_state = None
    for step in AddInspector.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу:\n{AddInspector.texts[previous_state.state]}")
            return
        previous_state = step


# GET USER NAME
@admin_router.message(ChangeUserInfo.change_user_event_registration_name,
                      or_f(F.text, F.text == "[Admin-user] Пропустить поле"))
async def admin_enter_name(message: Message, state: FSMContext):
    if message.text == "[Admin-user] Пропустить поле":
        await state.update_data(user_name=ChangeUserInfo.user_for_change.name)

    else:
        await state.update_data(user_name=message.text.lower())

    await message.answer("Измените номер телефона пользователя: ")
    # WAITING USER PHONE #
    await state.set_state(ChangeUserInfo.change_user_event_registration_phone)


# GET USER PHONE
@admin_router.message(ChangeUserInfo.change_user_event_registration_phone,
                      or_f(F.text, F.text == "[Admin-user] Пропустить поле"))
async def admin_enter_phone(message: Message, state: FSMContext):
    if message.text == "[Admin-user] Пропустить поле":
        await state.update_data(user_phone=ChangeUserInfo.user_for_change.phone)

    else:
        if not await validate_phone_input(message.text):
            await message.answer(
                "Некорректный формат номера телефона.\nПожалуйста, введите номер в формате +7(XXX)XXX-XX-XX.")
            return

        await state.update_data(user_phone=str(message.text))

    await message.answer("Измените email пользователя: ")
    # WAITING USER EMAIL #
    await state.set_state(ChangeUserInfo.change_user_event_registration_email)


# GET USER EMAIL
@admin_router.message(ChangeUserInfo.change_user_event_registration_email,
                      or_f(F.text, F.text == "[Admin-user] Пропустить поле"))
async def admin_enter_email(message: Message, state: FSMContext):
    if message.text == "[Admin-user] Пропустить поле":
        await state.update_data(user_email=ChangeUserInfo.user_for_change.email)

    else:
        user_email = await validate_email_input(message.text)  # Check date format is day-month-year
        if user_email is None:
            await message.answer("Некорректный формат почты.\nПожалуйста, введите почту в формате 'abcd123@gmail.com':")
            return

        await state.update_data(user_email=user_email)

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
async def admin_confirm(message: Message, state: FSMContext, session: AsyncSession, bot):
    data = await state.get_data()
    info = get_user_data_for_admin(data=data)

    user_id = ChangeUserInfo.user_for_change.tg_id
    user_name = ChangeUserInfo.user_for_change.name

    await orm_update_user(session=session, user_id=ChangeUserInfo.user_for_change.id, data=data, message=message)
    await orm_update_users_events(session=session, user_tg_id=ChangeUserInfo.user_for_change.tg_id, data=data)

    await message.answer("Пользователь изменен: ")
    await message.answer(f"{info}", reply_markup=start_admin_keyboard)

    # Send notification about changing user info
    await bot.send_message(user_id,
                           f"{user_name.title()}, данные о пользователе изменены!\n"
                           f"{info}",
                           reply_markup=start_admin_keyboard)

    await state.clear()
    ChangeUserInfo.user_for_change = None


# EVENT STUFF #
# Check Events
@admin_router.message(or_f(Command("event"), (F.text.lower() == "просмотр мероприятий")))
async def events_list(message: Message, session: AsyncSession):
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"Адрес мероприятия - {event.event_address}\n"
                             f"Id мероприятия - {event.id}\n"
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
async def close_event(callback: CallbackQuery, session: AsyncSession, bot):
    event_id = callback.data.split("_")[-1]
    event = await orm_get_events_id(session=session, event_id=int(event_id))

    for user in await orm_get_users_from_users_events(session=session, event_id=int(event_id)):
        await bot.send_message(user.user_tg_id,
                               f"{user.user_name.title()}, мероприятие {user.user_event_name} закрыто!")

    await orm_add_info_in_closed_events(session=session, event=event)  # Add closing event in closedEvents
    await orm_delete_event(session=session, event_id=int(event_id))  # Delete closing event from Events
    await orm_delete_event_from_users_events(session=session, event_id=int(event_id))  # Delete closing event from
    # usersEvents

    await callback.answer("Мероприятие закрыто!")
    await callback.message.answer("Мероприятие закрыто!")


# Delete Event
@admin_router.callback_query(F.data.startswith('delete_event_'))
async def delete_event(callback: CallbackQuery, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    await orm_delete_event(session=session, event_id=int(event_id))  # Delete closing event from Events
    await orm_delete_event_from_users_events(session=session, event_id=int(event_id))  # Delete closing event from
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
    await callback.message.answer("Измените название мероприятия: ",
                                  reply_markup=cancel_or_back_or_skip_for_add_event_admin)

    # WAITING USER NAME #
    await state.set_state(AddEvent.add_event_name)


# Event Name
@admin_router.message(AddEvent.add_event_name,
                      or_f(F.text, F.text == "[Admin-event] Пропустить поле"))
async def add_event_name(message: Message, state: FSMContext):
    if message.text == "[Admin-event] Пропустить поле":
        await state.update_data(event_name=AddEvent.event_for_change.event_name)

    else:
        await state.update_data(event_name=message.text.title())

    await message.answer("Введите адрес мероприятия: ")

    # WAITING EVENT DATE #
    await state.set_state(AddEvent.add_event_address)


# Event Address
@admin_router.message(AddEvent.add_event_address,
                      or_f(F.text, F.text == "[Admin-event] Пропустить поле"))
async def add_event_address(message: Message, state: FSMContext):
    if message.text == "[Admin-event] Пропустить поле":
        await state.update_data(event_address=AddEvent.event_for_change.event_address)

    else:
        event_address = await validate_address_input(message.text)

        if event_address is False:
            await message.answer("Некорректный формат адреса.\nПожалуйста, введите адрес в формате 'Офис 1, каб.101':")

            return

        await state.update_data(event_address=str(message.text))

    await message.answer("Введите дату мероприятия (дд-мм-гггг): ")

    # WAITING EVENT ADDRESS #
    await state.set_state(AddEvent.add_event_date)


# Event Date
@admin_router.message(AddEvent.add_event_date,
                      or_f(F.text, F.text == "[Admin-event] Пропустить поле"))
async def add_event_date(message: Message, state: FSMContext):
    if message.text == "[Admin-event] Пропустить поле":
        # date_obj = datetime.datetime.strptime(AddEvent.event_for_change.event_date, '%d-%m-%Y')
        # event_date_correct = date_obj.date()
        await state.update_data(event_date=AddEvent.event_for_change.event_date)

    else:
        event_date = await validate_date_input(message.text)  # Check date format is day-month-year
        if event_date is None:
            await message.answer("Некорректный формат даты.\nПожалуйста, введите дату в формате 'дд-мм-гггг':")
            return

        await state.update_data(event_date=str(event_date))

    await message.answer("Введите время мероприятия (часы:минуты): ")

    # WAITING EVENT DATE #
    await state.set_state(AddEvent.add_event_time)


# Event Time
@admin_router.message(AddEvent.add_event_time,
                      or_f(F.text, F.text == "[Admin-event] Пропустить поле"))
async def add_event_time(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "[Admin-event] Пропустить поле":
        await state.update_data(event_time=AddEvent.event_for_change.event_time)

    else:
        event_time = await validate_time_input(message.text)  # Check date format is day-month-year
        if event_time is None:
            await message.answer("Некорректный формат времени.\nПожалуйста, введите время в формате 'ч:м':")
            return

        await state.update_data(event_time=str(event_time))

    data = await state.get_data()
    event_name = data.get("event_name")
    event_address = data.get("event_address")
    event_date = data.get("event_date")
    event_time = data.get("event_time")
    info = get_event_info(data=data)

    original_event_name = AddEvent.event_for_change.event_name if AddEvent.event_for_change else ""

    same_event, reason = await no_same_event(session=session, event_name=event_name, event_address=event_address,
                                             event_date=event_date, event_time=event_time,
                                             original_event_name=original_event_name)

    if not same_event:
        await message.answer(reason, reply_markup=cancel_or_back_for_add_event_admin)
        return

    await message.answer("Мероприятие: \n"
                         f"{info}")

    # WAITING CONFIRM / CHANGE EVENT #
    await message.answer("Добавить мероприятие?",
                         reply_markup=confirm_or_change_event_info_by_admin)
    await state.set_state(AddEvent.confirm_or_change_event)


# Adding Event
# Adding Event
@admin_router.message(AddEvent.confirm_or_change_event, F.text.lower() == "добавить мероприятие")
async def add_event_time(message: Message, state: FSMContext, session: AsyncSession, bot):
    data = await state.get_data()

    info = get_event_info(data=data)

    if AddEvent.event_for_change:
        event_id = AddEvent.event_for_change.id

        # Update Events
        await orm_update_event(session=session, event_id=event_id, data=data)

        # Update usersEvents
        await orm_update_users_events_by_event_id(session=session, event_id=event_id, data=data)

        # Send notification about changing event
        for user in await orm_get_users_from_users_events(session=session, event_id=event_id):
            await bot.send_message(user.user_tg_id,
                                   f"{user.user_name.title()}, мероприятие {AddEvent.event_for_change.event_name}"
                                   f" изменено!\n"
                                   f"{info}")

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


# ADD ADMIN #
# Check Admins
@admin_router.message(F.text.lower() == "просмотр администраторов")
async def get_admins(message: Message, session: AsyncSession):
    await message.answer("Вот список администраторов: ")
    for admin in await orm_get_admins(session=session):
        await message.answer(f"tg_id - {admin.tg_id}\n"
                             f"Admin Name - {admin.name}\n"
                             f"Admin Phone - {admin.phone}\n"
                             f"Admin Email - {admin.email}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_admin_{admin.id}',
                                 'Удалить': f'delete_admin_{admin.tg_id}'
                             })
                             )


# Delete Admin
@admin_router.callback_query(F.data.startswith('delete_admin_'))
async def delete_admin(callback: CallbackQuery, session: AsyncSession):
    admin_id = callback.data.split("_")[-1]
    await orm_delete_admin(session=session, admin_id=int(admin_id))

    await callback.answer("Администратор удален")
    await callback.message.answer("Администратор удален!")


# Change admin
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_admin_'))
async def change_admin(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    admin_id = callback.data.split("_")[-1]
    admin_for_change = await orm_get_admin(session=session, admin_id=int(admin_id))

    AddAdmin.admin_for_change = admin_for_change

    await callback.answer()
    await callback.message.answer("Измените телеграм id администратора: ",
                                  reply_markup=cancel_or_back_for_admin_change_admin)

    # WAITING USER NAME #
    await state.set_state(AddAdmin.add_admin_tg_id)


# Add Admin
@admin_router.message(StateFilter(None), F.text.lower() == "добавить администратора")
async def add_admin(message: Message, state: FSMContext):
    await message.answer("Введите телеграм id администратора: ",
                         reply_markup=cancel_or_back_for_admin_admin)

    # WAIT TG ID #
    await state.set_state(AddAdmin.add_admin_tg_id)


# Admin tg id
@admin_router.message(AddAdmin.add_admin_tg_id, or_f(F.text,
                                                     F.text == "[Admin-admin] Пропустить поле"))
async def add_admin_tg_id(message: Message, state: FSMContext):
    if message.text == "[Admin-admin] Пропустить поле":
        await state.update_data(tg_id=AddAdmin.admin_for_change.tg_id)

    else:
        if not await validate_tg_id_input(tg_id=message.text):
            await message.answer(
                "Некорректный формат телеграм id.\nПожалуйста, введите телеграм id используя цифры.")
            return

        await state.update_data(admin_tg_id=message.text)

    await message.answer("Введите имя администратора: ")

    # WAITING ADMIN NAME #
    await state.set_state(AddAdmin.add_admin_name)


# Admin name
@admin_router.message(AddAdmin.add_admin_name, or_f(F.text,
                                                    F.text == "[Admin-admin] Пропустить поле"))
async def add_admin_name(message: Message, state: FSMContext):
    if message.text == "[Admin-admin] Пропустить поле":
        await state.update_data(admin_name=AddAdmin.admin_for_change.name)

    else:
        await state.update_data(admin_name=message.text.title())

    await message.answer("Введите телефон администратора: ")

    # WAITING ADMIN PHONE#
    await state.set_state(AddAdmin.add_admin_phone)


# Admin phone
@admin_router.message(AddAdmin.add_admin_phone, or_f(F.text,
                                                     F.text == "[Admin-admin] Пропустить поле"))
async def add_admin_phone(message: Message, state: FSMContext):
    if message.text == "[Admin-admin] Пропустить поле":
        await state.update_data(admin_phone=AddAdmin.admin_for_change.phone)

    else:
        if not await validate_phone_input(message.text):
            await message.answer(
                "Некорректный формат номера телефона.\nПожалуйста, введите номер в формате +7(XXX)XXX-XX-XX.")
            return

        await state.update_data(admin_phone=message.text)

    await message.answer("Введите эл.почту администратора: ")

    # WAITING ADMIN EMAIL#
    await state.set_state(AddAdmin.add_admin_email)


# Admin email
@admin_router.message(AddAdmin.add_admin_email, or_f(F.text,
                                                     F.text == "[Admin-admin] Пропустить поле"))
async def add_admin_email(message: Message, state: FSMContext):
    if message.text == "[Admin-admin] Пропустить поле":
        await state.update_data(admin_email=AddAdmin.admin_for_change.email)

    else:
        admin_email = await validate_email_input(message.text)
        if admin_email is None:
            await message.answer("Некорректный формат почты.\nПожалуйста, введите почту в формате 'abcd123@gmail.com':")
            return

        await state.update_data(admin_email=message.text)

    data = await state.get_data()

    info = get_admin_info(data=data)

    await message.answer("Данные администратора: ")
    await message.answer(f"{info}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Добавить администратора?",
                         reply_markup=confirm_or_change_admin_info_by_admin)
    await state.set_state(AddAdmin.confirm_or_change_admin)


# Admin adding
@admin_router.message(AddAdmin.confirm_or_change_admin,
                      F.text.lower() == "добавить администратора")
async def add_admin_confirm(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    info = get_admin_info(data=data)

    if AddAdmin.admin_for_change:
        admin_id = AddAdmin.admin_for_change.id

        # Update Events
        await orm_update_admin(session=session, admin_id=admin_id, data=data)

        await message.answer(f"Вы изменили администратора - {AddAdmin.admin_for_change.name}\n"
                             f"{info}",
                             reply_markup=start_admin_keyboard)

    else:
        await orm_admin_add_info(session=session, data=data)

        await message.answer("Добавлен администратор: ")
        await message.answer(f"{info}",
                             reply_markup=start_admin_keyboard)
    await state.clear()
    AddAdmin.admin_for_change = None


# ATTENDANCE
# Check Attendance
@admin_router.message(F.text.lower() == "просмотр посещений мероприятий")
async def attendance_list_admin(message: Message, session: AsyncSession):
    await message.answer("Список посещений:")
    for attendance in await orm_get_attendance(session=session):
        await message.answer(f"Телеграм id пользователя - {attendance.user_tg_id}\n"
                             f"Id мероприятия - {attendance.user_event_id}\n"
                             f"Название мероприятия - {attendance.user_event_name}\n"
                             f"Id проверяющего - {attendance.inspector_id}\n"
                             f"Заметки проверяющего - {attendance.inspector_notes}\n")


# INSPECTOR
# Check inspectors
@admin_router.message(F.text.lower() == "просмотр проверяющих")
async def get_inspectors(message: Message, session: AsyncSession):
    await message.answer("Вот список проверяющих: ")
    for inspector in await orm_get_inspectors(session=session):
        await message.answer(f"tg_id - {inspector.tg_id}\n"
                             f"Inspector Name - {inspector.name}\n"
                             f"Inspector Phone - {inspector.phone}\n"
                             f"Inspector Email - {inspector.email}\n",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_inspector_{inspector.id}',
                                 'Удалить': f'delete_inspector_{inspector.tg_id}'
                             })
                             )


# Delete Admin
@admin_router.callback_query(F.data.startswith('delete_inspector_'))
async def delete_inspector(callback: CallbackQuery, session: AsyncSession):
    inspector_id = callback.data.split("_")[-1]
    await orm_delete_inspector(session=session, inspector_id=int(inspector_id))

    await callback.answer("Проверяющий удален")
    await callback.message.answer("Проверяющий удален!")


# Change inspector
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_inspector_'))
async def change_inspector(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    inspector_id = callback.data.split("_")[-1]
    inspector_for_change = await orm_get_inspector(session=session, inspector_id=int(inspector_id))

    AddInspector.inspector_for_change = inspector_for_change

    await callback.answer()
    await callback.message.answer("Измените телеграм id проверяющего: ",
                                  reply_markup=cancel_or_back_for_admin_change_inspector)

    # WAITING USER NAME #
    await state.set_state(AddInspector.add_inspector_tg_id)


# Add inspector
@admin_router.message(StateFilter(None), F.text.lower() == "добавить проверяющего")
async def add_inspector(message: Message, state: FSMContext):
    await message.answer("Введите телеграм id проверяющего: ",
                         reply_markup=cancel_or_back_for_admin_inspector)

    # WAIT TG ID #
    await state.set_state(AddInspector.add_inspector_tg_id)


# Inspector tg id
@admin_router.message(AddInspector.add_inspector_tg_id, or_f(F.text,
                                                             F.text == "[Admin-inspector] Пропустить поле"))
async def add_inspector_tg_id(message: Message, state: FSMContext):
    if message.text == "[Admin-inspector] Пропустить поле":
        await state.update_data(tg_id=AddInspector.inspector_for_change.tg_id)

    else:
        if not await validate_tg_id_input(tg_id=message.text):
            await message.answer(
                "Некорректный формат телеграм id.\nПожалуйста, введите телеграм id используя цифры.")
            return

        await state.update_data(tg_id=message.text)

    await message.answer("Введите имя проверяющего: ")

    # WAITING INSPECTOR NAME #
    await state.set_state(AddInspector.add_inspector_name)


# Inspector name
@admin_router.message(AddInspector.add_inspector_name, or_f(F.text,
                                                            F.text == "[Admin-inspector_] Пропустить поле"))
async def add_inspector__name(message: Message, state: FSMContext):
    if message.text == "[Admin-inspector_] Пропустить поле":
        await state.update_data(inspector_name=AddInspector.inspector_for_change.name)

    else:
        await state.update_data(inspector_name=message.text.title())

    await message.answer("Введите телефон проверяющего: ")

    # WAITING ADMIN PHONE#
    await state.set_state(AddInspector.add_inspector_phone)


# Inspector phone
@admin_router.message(AddInspector.add_inspector_phone, or_f(F.text,
                                                             F.text == "[Admin-inspector] Пропустить поле"))
async def add_inspector_phone(message: Message, state: FSMContext):
    if message.text == "[Admin-inspector] Пропустить поле":
        await state.update_data(inspector_phone=AddInspector.inspector_for_change.phone)

    else:
        if not await validate_phone_input(message.text):
            await message.answer(
                "Некорректный формат номера телефона.\nПожалуйста, введите номер в формате +7(XXX)XXX-XX-XX.")
            return

        await state.update_data(inspector_phone=message.text)

    await message.answer("Введите эл.почту проверяющего: ")

    # WAITING INSPECTOR EMAIL#
    await state.set_state(AddInspector.add_inspector_email)


# Inspector email
@admin_router.message(AddInspector.add_inspector_email, or_f(F.text,
                                                             F.text == "[Admin-inspector] Пропустить поле"))
async def add_inspector_email(message: Message, state: FSMContext):
    if message.text == "[Admin-inspector] Пропустить поле":
        await state.update_data(inspector_email=AddInspector.inspector_for_change.email)

    else:
        inspector_email = await validate_email_input(message.text)
        if inspector_email is None:
            await message.answer("Некорректный формат почты.\nПожалуйста, введите почту в формате 'abcd123@gmail.com':")
            return

        await state.update_data(inspector_email=message.text)

    data = await state.get_data()

    info = get_inspector_info(data=data)

    await message.answer("Данные проверяющего: ")
    await message.answer(f"{info}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Добавить проверяющего?",
                         reply_markup=confirm_or_change_inspector_info_by_admin)
    await state.set_state(AddInspector.confirm_or_change_inspector)


# Inspector adding
@admin_router.message(AddInspector.confirm_or_change_inspector,
                      F.text.lower() == "добавить проверяющего")
async def add_inspector_confirm(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    info = get_inspector_info(data=data)

    if AddInspector.inspector_for_change:
        inspector_id = AddInspector.inspector_for_change.id

        # Update Events
        await orm_update_inspector(session=session, inspector_id=inspector_id, data=data)

        await message.answer(f"Вы изменили проверяющего - {AddInspector.inspector_for_change.name}\n"
                             f"{info}",
                             reply_markup=start_admin_keyboard)

        AddInspector.inspector_for_change = None

    else:
        await orm_inspector_add_info(session=session, data=data)

        await message.answer("Добавлен проверяющий: ")
        await message.answer(f"{info}",
                             reply_markup=start_admin_keyboard)

        AddInspector.inspector_for_change = None

    await state.clear()
    AddInspector.inspector_for_change = None

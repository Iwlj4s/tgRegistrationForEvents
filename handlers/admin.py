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
from keyboards.reply import (start_registration_keyboard, start_admin_keyboard, get_keyboard,
                             confirm_or_change_user_info_by_admin)
from keyboards.inline import get_callback_btns

from user_data.get_user_info import get_user_info, get_user_data_for_admin

from checks.check_user_input import user_input_id_event_is_correct

from database.models import Admins
from database.orm_query import orm_get_users, orm_delete_user, orm_get_events, orm_get_user, orm_user_add_info, \
    orm_update_user, orm_delete_user_from_events, orm_update_users_events

admin_router = Router()


class ChangeUserInfo(StatesGroup):
    # user_choose_event_registration = State()
    user_event_registration_event = State()
    user_event_registration_name = State()
    user_event_registration_phone = State()
    user_event_registration_email = State()

    user_event_registration_change_or_confirm = State()

    user_for_change = None

    texts = {
        'UserRegistration:user_event_registration_name': 'Измените имя пользователя: ',
        'UserRegistration:user_event_registration_phone': 'Измените телефон пользователя: ',
        'UserRegistration:user_event_registration_email': 'Измените email пользователя: '
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


# Check Users #
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
                                 'Изменить': f'change_{user.id}',
                                 'Удалить': f'delete_{user.tg_id}'
                             })
                             )


# Check Events
@admin_router.message(or_f(Command("event"), (F.text.lower() == "просмотр мероприятий")))
async def events_list(message: Message, session: AsyncSession):
    await message.answer("Список мероприятий:")
    for event in await orm_get_events(session=session):
        await message.answer(f"{event.event_name}\n"
                             f"User event_id - {event.id}\n"
                             f"Дата мероприятия - {event.event_date}\n"
                             f"Начало мероприятия - {event.event_time}\n")


# Delete User
@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_user(callback: CallbackQuery, session: AsyncSession):
    print("Delete function start !")
    user_id = callback.data.split("_")[-1]
    await orm_delete_user(session=session, user_id=int(user_id))
    await orm_delete_user_from_events(session=session, user_id=int(user_id))

    await callback.answer("Пользователь удален")
    await callback.message.answer("Пользователь удален!")


# CANCEL #
@admin_router.message(StateFilter('*'), F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    if ChangeUserInfo.user_for_change:
        ChangeUserInfo.user_for_change = None

    await state.clear()
    await message.answer("Все действия отменены", reply_markup=start_admin_keyboard)


# BACK #
@admin_router.message(StateFilter('*'), F.text.lower() == "изменить предыдущее поле")
@admin_router.message(StateFilter('*'), Command("Изменить предыдущее поле"))
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == ChangeUserInfo.user_event_registration_name:
        await message.answer("Предыдущего шага нет, введите свое имя или нажмите 'отмена' ")
        return

    previous_state = None
    for step in ChangeUserInfo.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу\n"
                                 f"{ChangeUserInfo.texts[previous_state.state]}")
            return
        previous_state = step


# Change user
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_user(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.data.split("_")[-1]
    user_for_change = await orm_get_user(session=session, user_id=int(user_id))

    ChangeUserInfo.user_for_change = user_for_change

    await callback.answer()
    await callback.message.answer("Измените имя пользователя: ",
                                  reply_markup=get_keyboard(
                                      "изменить предыдущее поле",
                                      "отмена"
                                  ))

    # WAITING USER NAME #
    await state.set_state(ChangeUserInfo.user_event_registration_name)


# GET USER NAME #
@admin_router.message(ChangeUserInfo.user_event_registration_name, F.text)
async def admin_enter_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text.lower())

    await message.answer("Измените номер телефона пользователя: ")
    # WAITING USER PHONE #
    await state.set_state(ChangeUserInfo.user_event_registration_phone)


# GET USER PHONE #
@admin_router.message(ChangeUserInfo.user_event_registration_phone, F.text)
async def admin_enter_name(message: Message, state: FSMContext):

    await state.update_data(user_phone=message.text)

    await message.answer("Измените email пользователя: ")
    # WAITING USER EMAIL #
    await state.set_state(ChangeUserInfo.user_event_registration_email)


# GET USER EMAIL #
@admin_router.message(ChangeUserInfo.user_event_registration_email, F.text)
async def admin_enter_name(message: Message, state: FSMContext):

    await state.update_data(user_email=message.text)
    data = await state.get_data()

    info = get_user_info(data=data)

    await message.answer("Данные для изменения информации: ")
    await message.answer(f"{info}")

    # WAITING CONFIRM / CHANGE INFO #
    await message.answer("Изменить информацию?",
                         reply_markup=confirm_or_change_user_info_by_admin)
    await state.set_state(ChangeUserInfo.user_event_registration_change_or_confirm)


# CONFIRM INFO #
@admin_router.message(ChangeUserInfo.user_event_registration_change_or_confirm,
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


# GET USER EVENT #
@admin_router.message(ChangeUserInfo.user_event_registration_event, F.text)
async def admin_enter_event(message: Message, state: FSMContext, session: AsyncSession):

    if not await user_input_id_event_is_correct(session=session, event_id=message.text):
        await message.answer("Введите корректный id мероприятия\n"
                             "/event - мероприятия", reply_markup=start_registration_keyboard)
        return

    await state.update_data(event_id=message.text)

    await message.answer("Измените имя пользователя: ",
                         reply_markup=get_keyboard(
                             "изменить предыдущее поле",
                             "отмена"
                         ))

    # WAITING ... #
    await state.set_state()

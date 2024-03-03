# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message

# SqlAlchemy Imports #
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# My Imports #
from keyboards.reply import start_registration_keyboard, start_admin_keyboard
from keyboards.inline import get_callback_btns

from database.models import Admins
from database.orm_query import orm_get_users, orm_delete_user

admin_router = Router()


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
                             f"User event_id - {user.event_id}\n"
                             f"User Name - {user.name}\n"
                             f"User Phone - {user.phone}\n"
                             f"User Email - {user.email}\n"
                             f"User Event - {user.event}",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_{user.id}',
                                 'Удалить': f'delete_{user.id}'
                             })
                             )


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_user(callback: CallbackQuery, session: AsyncSession):
    print("Delete function start !")
    user_id = callback.data.split("_")[-1]
    await orm_delete_user(session=session, user_id=int(user_id))

    await callback.answer("Пользователь удален")
    await callback.message.answer("Пользователь удален!")

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
from database.orm_query import orm_get_user_by_tg_id

from checks.check_user_input import user_id_already_in_db

from keyboards.reply import start_inspector_keyboard, after_registration_user_keyboard, start_registration_keyboard

inspector_router = Router()


# Start For Inspector#
@inspector_router.message(Command("inspector"))
async def inspector_login(message: Message, session: AsyncSession, bot):
    db_inspector = select(Inspectors.tg_id)
    inspectors = await session.execute(db_inspector)

    inspector_ids = [inspector[0] for inspector in inspectors]

    print(f"Admin_db: {inspector_ids}")
    print(f"Msg from user: {message.from_user.id}")

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
import asyncio
import logging
import os

from dotenv import load_dotenv

# Aiogram Imports #
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault


# My Imports #
from handlers.user_register import user_registration_router
from handlers.admin import admin_router
from handlers.inspector import inspector_router

from bot_commands.bot_commands_list import user_commands

load_dotenv()

from database.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession


# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']
token = os.getenv("TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

dp.include_router(user_registration_router)
dp.include_router(admin_router)
dp.include_router(inspector_router)


async def startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def shutdown(bot):
    print("Bot down")


async def main():
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.set_my_commands(commands=user_commands, scope=BotCommandScopeDefault())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

import asyncio
import logging
import os

from dotenv import load_dotenv

# Aiogram Imports #
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault

# My Imports #
from handlers.user_register import user_registration_router

from bot_commands.bot_commands_list import user_commands

load_dotenv()

ALLOWED_UPDATES = ['message', 'edited_message']
token = os.getenv("TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

dp.include_router(user_registration_router)


async def main():
    await bot.set_my_commands(commands=user_commands, scope=BotCommandScopeDefault())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

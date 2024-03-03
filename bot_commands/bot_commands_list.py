from aiogram.types import BotCommand

user_commands = [
    BotCommand(command="event_registration", description="Регистрация на мероприятие"),
    BotCommand(command="event", description="список мероприятий"),
]

# If commands change:
# await bot.delete_my_commands(scope=BotCommandScopeDefault())
# await bot.set_my_commands(commands=private, scope=BotCommandScopeDefault())
# for reset commands

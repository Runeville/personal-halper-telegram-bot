from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("You can send me those commands and I will execute them: ",
            "/start - Starts dialog with Jake",
            "/help - Gives help information",
            "/convert - Converts currency",
            "/playlists - Shows YouTube playlists you currently watching")
    
    await message.answer("\n".join(text))

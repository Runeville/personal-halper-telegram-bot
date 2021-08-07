import sqlite3

import sqlalchemy.exc
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from handlers.users.db_manager import DBManager


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Hey, Dude!")

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    user_id = int(message.from_user.id)
    try:
        user = DBManager()
        user.create_user(user_id, first_name, last_name, username)
    except sqlalchemy.exc.IntegrityError:
        pass

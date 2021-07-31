from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from keyboards.inline.choice_buttons import physics_navigation
from loader import dp


@dp.message_handler(Command("physics"))
async def show_physics(message: Message):
    await message.answer(text="https://www.youtube.com/watch?v=eZy2wp5XINY&list=PL1Us50cZo25m2FDcpykgjCCZQ3SFAsG3y&index=8",
                         reply_markup=physics_navigation)


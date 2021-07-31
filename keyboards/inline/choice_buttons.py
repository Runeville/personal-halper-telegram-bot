from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import physics_callback

physics_navigation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="<<", callback_data=physics_callback.new(
                direction="prev"
            )),
            InlineKeyboardButton(text=">>", callback_data=physics_callback.new(
                direction="next"
            )),
        ],
        [
            InlineKeyboardButton(text="Back", callback_data="cancel")
        ]
    ]
)


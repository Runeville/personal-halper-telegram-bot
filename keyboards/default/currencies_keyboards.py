from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


currencies_to_convert = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="rub")
        ],
        [
            KeyboardButton(text="usd"),
            KeyboardButton(text="euro")
        ]
    ],
    resize_keyboard=True
)
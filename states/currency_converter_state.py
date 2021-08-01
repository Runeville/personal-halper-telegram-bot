from aiogram.dispatcher.filters.state import StatesGroup, State


class CurrencyConverterState(StatesGroup):
    currency = State()
    currency_2 = State()
    currency_3 = State()

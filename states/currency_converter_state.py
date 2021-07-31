from aiogram.dispatcher.filters.state import StatesGroup, State


class CurrencyConverterState(StatesGroup):
    currency = State()

from aiogram.dispatcher.filters.state import StatesGroup, State


class PlaylistsStates(StatesGroup):
    link = State()
    title = State()

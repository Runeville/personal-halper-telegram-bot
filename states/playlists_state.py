from aiogram.dispatcher.filters.state import StatesGroup, State


class PlaylistsStates(StatesGroup):
    link = State()
    title = State()


class PlaylistsDeleteStates(StatesGroup):
    delete = State()


class PlaylistsEditStates(StatesGroup):
    edit = State()

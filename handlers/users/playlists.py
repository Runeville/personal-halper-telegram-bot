from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

import googleapiclient.discovery as g_disc
import googleapiclient.errors
from urllib.parse import parse_qs, urlparse

from data.config import YOUTUBE_API_KEY

from loader import dp
from states.playlists_state import PlaylistsStates
from handlers.users.db_manager import DBManager


@dp.message_handler(Command("playlists"))
async def get_playlist_link(message: Message):
    await message.answer(text="Give me a link.")
    await PlaylistsStates.first()


@dp.message_handler(state=PlaylistsStates.link)
async def get_playlist_title(message: Message, state: FSMContext):
    url: str = message.text.strip()
    await message.answer("One sec, bro.")

    # Trying to connect to this url
    try:
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        youtube = g_disc.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )

    # Handling exceptions
    except KeyError:
        await message.answer(text="Seems like you you sent me some bullshit when I requested a link.")
    except googleapiclient.errors.HttpError:
        await message.answer(text="Hey, you know. I can't really connect using this link.")
        await state.finish()

    else:
        await message.answer(text="How do you want me to call this playlist?")

        async with state.proxy() as data:
            data['link'] = message.text
            data['videos'] = []
            while request is not None:
                response = request.execute()
                data['videos'] += response['items']
                request = youtube.playlistItems().list_next(request, response)

        await PlaylistsStates.next()


@dp.message_handler(state=PlaylistsStates.title)
async def create_playlist(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text.strip()

        playlist = DBManager()
        user_telegram_id = int(playlist.select_user_by_telegram_id(message.from_user.id).id)
        playlist.create_playlist(data['title'], data['videos'], user_telegram_id)

    await message.answer(text='Yeah! I\'ve created your playlist! To check it type "/playlists"')

    await state.finish()



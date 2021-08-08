from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import googleapiclient.discovery as g_disc
import googleapiclient.errors
from urllib.parse import parse_qs, urlparse

from data.config import YOUTUBE_API_KEY
from keyboards.inline.callback_datas import playlists_callback
from keyboards.inline.playlists_buttons import playlists_navigation, get_videos_navigation

from loader import dp
from states.playlists_state import PlaylistsStates, PlaylistsDeleteStates, PlaylistsEditStates
from handlers.users.db_manager import DBManager


@dp.message_handler(state=PlaylistsStates.link)
async def get_playlist_title(message: Message, state: FSMContext):
    url: str = message.text.strip()

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
        await state.finish()
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


@dp.message_handler(state=PlaylistsEditStates.edit)
async def edit_playlist(message: Message, state: FSMContext):
    playlist_title = message.text.strip()
    playlist_state = await state.get_data()
    DBManager().edit_playlist(playlist_state['playlist_id'], playlist_title)
    await message.answer(text="Playlist name was changed.")

    await state.finish()


@dp.message_handler(state=PlaylistsDeleteStates.delete)
async def delete_playlist(message: Message, state: FSMContext):
    playlist_title = message.text.strip()
    playlist_state = await state.get_data()
    if playlist_title == DBManager().select_playlist_by_id(playlist_state['playlist_id'])['title']:
        DBManager().delete_playlist(playlist_state['playlist_id'])
        await message.answer(text="This playlist will no longer bother you...")
    else:
        await message.answer(text="Names doesn't match.")
    await state.finish()


@dp.message_handler(state=PlaylistsStates.title)
async def create_playlist(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text.strip()

        playlist = DBManager()
        user_id = int(message.from_user.id)
        playlist.create_playlist(data['title'], data['videos'], user_id)

    await message.answer(text='Yeah! I\'ve created your playlist! To check it type "/playlists"')

    await state.finish()


@dp.message_handler(Command("playlists"))
async def get_playlist_link(message: Message):
    user_id = int(message.from_user.id)

    await message.answer(text="Here's you playlists, dude.", reply_markup=playlists_navigation(user_id))


@dp.callback_query_handler(playlists_callback.filter())
async def video_handler(call: CallbackQuery, callback_data: dict):
    if callback_data['method'] == "create":
        await call.message.answer(text="Give me a link to YouTube playlist.")
        await PlaylistsStates.first()

    elif callback_data['method'] == "edit":
        playlist = DBManager().select_playlist_by_id(callback_data['playlist_id'])
        await call.message.answer(f"How do you want to rename it?")

        await PlaylistsEditStates.first()

        state = dp.current_state(chat=call.message.chat.id, user=call.from_user.id)
        await state.update_data(playlist_id=playlist['id'])

    elif callback_data['method'] == "delete":
        playlist = DBManager().select_playlist_by_id(callback_data['playlist_id'])
        await call.message.answer(f"Boy, to delete this, please type <b>{playlist['title']}</b> to confirm.")

        await PlaylistsDeleteStates.first()

        state = dp.current_state(chat=call.message.chat.id, user=call.from_user.id)
        await state.update_data(playlist_id=playlist['id'])

    elif callback_data['method'] == 'watch':
        if callback_data['direction'] == "0":
            video = DBManager().select_current_video_by_playlist_id(playlist_id=int(callback_data['playlist_id']))

            await call.message.answer(text=f"{video.title}\n"
                                           f"{video.link}",
                                      reply_markup=get_videos_navigation(callback_data['playlist_id']))
        else:
            if callback_data['direction'] == "next":
                video = DBManager().switch_video(callback_data['playlist_id'])
            else:
                video = DBManager().switch_video(callback_data['playlist_id'], False)

            await call.message.answer(text=f"{video.title}\n"
                                           f"{video.link}",
                                      reply_markup=get_videos_navigation(callback_data['playlist_id']))

    await call.message.delete()

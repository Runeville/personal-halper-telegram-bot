from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import playlists_callback
from handlers.users.db_manager import DBManager


def make_callback(method, playlist_id="0", direction="0"):
    return playlists_callback.new(method=method, playlist_id=playlist_id, direction=direction)


def playlists_navigation(user_id):
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup()

    playlists = DBManager().select_playlists_by_user_id(user_id=user_id)
    for playlist in playlists:
        videos = DBManager().select_videos_by_playlist_id(playlist['id'])
        current_video = DBManager().select_current_video_by_playlist_id(playlist['id'])['serial_number']
        markup.add(
            InlineKeyboardButton(text=f"{playlist.title} — {current_video}/{len(videos)}",
                                 callback_data=make_callback("watch", playlist_id=playlist.id))
        )

    markup.add(InlineKeyboardButton(text="Create new playlist", callback_data=make_callback("create")))
    markup.insert(InlineKeyboardButton(text="Cancel", callback_data=make_callback("cancel")))

    return markup


def get_videos_navigation(playlist_id):
    markup = InlineKeyboardMarkup()

    current_video = DBManager().select_current_video_by_playlist_id(playlist_id=playlist_id)
    prev_video = DBManager().select_video_by_its_serial_number(playlist_id, int(current_video['serial_number']) - 1)
    next_video = DBManager().select_video_by_its_serial_number(playlist_id, int(current_video['serial_number']) + 1)

    if prev_video:
        markup.add(InlineKeyboardButton(text="<<", callback_data=make_callback("watch", playlist_id, "previous")))
    if next_video:
        markup.insert(InlineKeyboardButton(text=">>",
                                           callback_data=make_callback("watch", playlist_id, "next")))
    markup.add(InlineKeyboardButton(text="Cancel", callback_data=make_callback("cancel")))

    return markup


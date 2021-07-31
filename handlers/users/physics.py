from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from data.config import DATA_DIR
from keyboards.inline.choice_buttons import physics_navigation
from loader import dp

import pandas as pd

current_video: pd.Series
csv_filename = "videos.csv"


# Gets a video I watch currently
def get_video():
    global current_video
    df = pd.read_csv(DATA_DIR + csv_filename)
    for index, row in df.iterrows():
        if row['watched'] == "No":
            current_video = row
            current_video['index'] = index
            return current_video
    return None


# Goes to next or previous video and changes 'watched' status of current or previous video
def change_current_video(is_next=True):
    df = pd.read_csv(DATA_DIR + csv_filename)
    video = get_video()
    if video is not None:
        if is_next:
            df.at[video['index'], 'watched'] = "Yes"
        else:
            try:
                df.at[video['index'] - 1, 'watched'] = "No"
            except:
                pass
        df.to_csv(DATA_DIR + csv_filename, index=False)
    return get_video()


@dp.message_handler(Command("physics"))
async def show_physics(message: Message):
    video = get_video()
    if video is not None:
        await message.answer(text=f"{video['title']}\n"
                                  f"{video['link']}",
                             reply_markup=physics_navigation)
    else:
        await message.answer(text="Seems you have watched all the videos from this playlist.")


@dp.callback_query_handler(text_contains="next")
async def next_video(call: CallbackQuery):
    await call.answer(cache_time=60)
    video = change_current_video()

    await call.message.answer(text=f"{video['title']}\n"
                                   f"{video['link']}",
                              reply_markup=physics_navigation)
    await call.message.delete()


@dp.callback_query_handler(text_contains="prev")
async def next_video(call: CallbackQuery):
    await call.answer(cache_time=60)
    video = change_current_video(is_next=False)

    await call.message.answer(text=f"{video['title']}\n"
                                   f"{video['link']}",
                              reply_markup=physics_navigation)
    await call.message.delete()


@dp.callback_query_handler(text_contains="cancel")
async def close_playlist(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.delete()

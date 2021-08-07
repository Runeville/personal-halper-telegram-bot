from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Start dialog with Jake"),
            types.BotCommand("help", "Show help"),
            types.BotCommand("convert", "Convert currency"),
            types.BotCommand("playlists", "Show playlists")
        ]
    )

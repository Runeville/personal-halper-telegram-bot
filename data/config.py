import os

from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()


BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\data", "")

DB_NAME = "bot_db.db"

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста
YOUTUBE_API_KEY = env.str("YOUTUBE_API_KEY")

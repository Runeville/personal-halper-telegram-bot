from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String, Boolean, ForeignKey

from data.config import BASE_DIR, DB_NAME


class DBManager:
    meta = MetaData()

    users = Table(
        "Users", meta,
        Column("id", Integer, primary_key=True),
        Column("first_name", String(250), nullable=False),
        Column("last_name", String(250), nullable=False),
        Column("telegram_id", Integer, nullable=False),
        Column("username", String(250), nullable=False)
    )

    playlists = Table(
        "Playlists", meta,
        Column("id", Integer, primary_key=True),
        Column("title", String(250), nullable=False),
        Column("user_id", Integer, ForeignKey("Users.id"))
    )

    videos = Table(
        "Videos", meta,
        Column("id", Integer, primary_key=True),
        Column("title", String(250), nullable=False),
        Column("link", String(500), nullable=False),
        Column("is_watched", Boolean, default=False),
        Column("playlist_id", Integer, ForeignKey("Playlists.id"))
    )

    def __init__(self):
        engine = create_engine(f"sqlite:///{BASE_DIR}/{DB_NAME}")
        self.meta.create_all(engine)

        self.connection = engine.connect()

    def create_user(self, first_name: str, last_name: str, username: str, user_id: int):
        add_user = self.users.insert().values(first_name=first_name, last_name=last_name, username=username,
                                              telegram_id=user_id)
        self.connection.execute(add_user)

    def create_playlist(self, name: str, videos: list, user_id: int):
        add_playlist = self.playlists.insert().values(title=name, user_id=user_id)
        playlist_id = self.connection.execute(add_playlist).lastrowid

        for video in videos:
            title = video['snippet']['title']

            if title != "Private video":
                link = f'https://www.youtube.com/watch?v={video["snippet"]["resourceId"]["videoId"]}'
                add_video = self.videos.insert().values(title=title,
                                                        link=link,
                                                        playlist_id=playlist_id)
                self.connection.execute(add_video)

    def select_user_by_telegram_id(self, telegram_id: int):
        s = self.users.select().where(self.users.c.telegram_id == telegram_id)
        s = self.connection.execute(s)
        for i in s:
            return i

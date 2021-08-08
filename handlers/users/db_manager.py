from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String, Boolean, ForeignKey

from data.config import BASE_DIR, DB_NAME


class DBManager:
    meta = MetaData()

    users = Table(
        "Users", meta,
        Column("id", Integer, nullable=False, unique=True),
        Column("first_name", String(250), nullable=False),
        Column("last_name", String(250), nullable=False),
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
        Column("serial_number", Integer, nullable=False),
        Column("is_watched", Boolean, default=False),
        Column("playlist_id", Integer, ForeignKey("Playlists.id"))
    )

    def __init__(self):
        engine = create_engine(f"sqlite:///{BASE_DIR}/{DB_NAME}")
        self.meta.create_all(engine)

        self.connection = engine.connect()

    def create_user(self, user_id: int, first_name: str, last_name: str, username: str):
        add_user = self.users.insert().values(id=user_id, first_name=first_name, last_name=last_name, username=username)
        self.connection.execute(add_user)

    def create_playlist(self, name: str, videos: list, user_id: int):
        add_playlist = self.playlists.insert().values(title=name, user_id=user_id)
        playlist_id = self.connection.execute(add_playlist).lastrowid
        serial_number = 0
        for video in videos:
            title = video['snippet']['title']

            if title != "Private video":
                serial_number += 1
                link = f'https://www.youtube.com/watch?v={video["snippet"]["resourceId"]["videoId"]}'
                add_video = self.videos.insert().values(title=title,
                                                        link=link,
                                                        playlist_id=playlist_id,
                                                        serial_number=serial_number)
                self.connection.execute(add_video)

    def select_playlist_by_id(self, playlist_id):
        playlist = self.playlists.select().where(self.playlists.c.id == playlist_id)
        playlist = self.connection.execute(playlist).first()

        return playlist

    def select_playlists_by_user_id(self, user_id):
        s = self.playlists.select().where(self.playlists.c.user_id == user_id)
        playlists = self.connection.execute(s).all()

        return playlists

    def delete_playlist(self, playlist_id):
        playlist = self.playlists.delete().where(self.playlists.c.id == playlist_id)
        self.connection.execute(playlist)

        videos = self.videos.delete().where(self.videos.c.playlist_id == playlist_id)
        self.connection.execute(videos)

    def select_videos_by_playlist_id(self, playlist_id):
        s = self.videos.select().where(self.videos.c.playlist_id == playlist_id)
        videos = self.connection.execute(s).all()

        return videos

    def select_current_video_by_playlist_id(self, playlist_id):
        current_video = self.videos.select().where(self.videos.c.playlist_id == playlist_id,
                                                   self.videos.c.is_watched == False)
        current_video = self.connection.execute(current_video).first()

        return current_video

    def select_video_by_its_serial_number(self, playlist_id, serial_number):
        video = self.videos.select(). \
            where(self.videos.c.playlist_id == playlist_id, self.videos.c.serial_number == serial_number)
        video = self.connection.execute(video).first()
        return video

    def switch_video(self, playlist_id, is_next=True):
        serial_number = int(self.select_current_video_by_playlist_id(playlist_id).serial_number)

        if is_next:
            video = self.videos.update().where(self.videos.c.playlist_id == playlist_id,
                                               self.videos.c.serial_number == serial_number).values(is_watched=True)
        else:
            video = self.videos.update().where(self.videos.c.playlist_id == playlist_id,
                                               self.videos.c.serial_number == serial_number - 1).values(
                is_watched=False)
        self.connection.execute(video)

        video = self.select_current_video_by_playlist_id(playlist_id)
        return video

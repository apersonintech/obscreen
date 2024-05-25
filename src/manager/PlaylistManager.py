import os

from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Playlist import Playlist
from src.utils import get_optional_string, get_yt_video_id, slugify
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.service.ModelManager import ModelManager


class PlaylistManager(ModelManager):

    TABLE_NAME = "playlist"
    TABLE_MODEL = [
        "name CHAR(255)",
        "slug CHAR(255)",
        "enabled INTEGER DEFAULT 0",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager):
        super().__init__(lang_manager, database_manager, user_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_playlist: dict, id: int = None) -> Playlist:
        if id:
            raw_playlist['id'] = id

        [raw_playlist, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_playlist)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(self.TABLE_NAME, raw_playlist['id'], user_tracker_edits)

        return Playlist(**raw_playlist)

    def hydrate_list(self, raw_playlists: list) -> List[Playlist]:
        return [self.hydrate_object(raw_playlist) for raw_playlist in raw_playlists]

    def get(self, id: Optional[int]) -> Optional[Playlist]:
        if not id:
            return None

        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None, values: dict = {}) -> List[Playlist]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort, values=values))

    def get_one_by(self, query, values: dict = {}) -> Optional[Playlist]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query, values=values)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_durations_by_playlists(self):
        durations = self._db.execute_read_query("select playlist, sum(duration) as total_duration from slideshow where cron_schedule is null group by playlist")
        map = {}
        for duration in durations:
            map[duration['playlist']] = duration['total_duration']
        return map

    def get_all(self) -> List[Playlist]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME))

    def get_enabled_playlists(self, with_default: bool = False) -> List[Playlist]:
        playlists = self.get_by(query="enabled = 1")

        if not with_default:
            return playlists

        return [Playlist(id=None, name=self.t('slideshow_playlist_panel_item_default'))] + playlists

    def get_disabled_playlists(self) -> List[Playlist]:
        return self.get_by(query="enabled = 0")

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"enabled": enabled})

    def forget_user(self, user_id: int):
        playlists = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_playlists = self.user_manager.forget_user(playlists, user_id)

        for playlist_id, edits in edits_playlists.items():
            self._db.update_by_id(self.TABLE_NAME, playlist_id, edits)

    def pre_add(self, playlist: Dict) -> Dict:
        playlist["slug"] = slugify(playlist["name"])
        self.user_manager.track_user_on_create(playlist)
        self.user_manager.track_user_on_update(playlist)
        return playlist

    def pre_update(self, playlist: Dict) -> Dict:
        playlist["slug"] = slugify(playlist["name"])
        self.user_manager.track_user_on_update(playlist)
        return playlist

    def pre_delete(self, playlist_id: str) -> str:
        return playlist_id

    def post_add(self, playlist_id: str) -> str:
        return playlist_id

    def post_update(self, playlist_id: str) -> str:
        return playlist_id

    def post_updates(self):
        pass

    def post_delete(self, playlist_id: str) -> str:
        return playlist_id

    def update_form(self, id: int, name: str) -> None:
        playlist = self.get(id)

        if not playlist:
            return

        form = {
            "name": name
        }

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)

    def add_form(self, playlist: Union[Playlist, Dict]) -> None:
        form = playlist

        if not isinstance(playlist, dict):
            form = playlist.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(playlist.id)

    def delete(self, id: int) -> None:
        playlist = self.get(id)

        if playlist:
            self.pre_delete(id)
            self._db.delete_by_id(self.TABLE_NAME, id)
            self.post_delete(id)

    def to_dict(self, playlists: List[Playlist]) -> List[Dict]:
        return [playlist.to_dict() for playlist in playlists]


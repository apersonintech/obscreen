import os

from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Playlist import Playlist
from src.util.utils import get_optional_string, get_yt_video_id, slugify, slugify_next
from src.manager.DatabaseManager import DatabaseManager
from src.manager.SlideManager import SlideManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager


class PlaylistManager(ModelManager):

    TABLE_NAME = "playlist"
    TABLE_MODEL = [
        "name CHAR(255)",
        "slug CHAR(255)",
        "enabled INTEGER DEFAULT 0",
        "fallback INTEGER DEFAULT 0",
        "time_sync INTEGER DEFAULT 1",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)
        self.check_and_set_fallback()

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

    def get_one_by(self, query, values: dict = {}, sort: Optional[str] = None, ascending=True, limit: Optional[int] = None) -> Optional[Playlist]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query, values=values, sort=sort, ascending=ascending, limit=limit)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_durations_by_playlists(self, playlist_id: Optional[int] = None):
        durations = self._db.execute_read_query("select playlist_id, sum(duration) as total_duration from {} where cron_schedule is null {} group by playlist_id".format(
            SlideManager.TABLE_NAME,
            "{}".format(
                " AND playlist_id = {}".format(playlist_id) if playlist_id else ""
            )
        ))
        map = {}
        for duration in durations:
            map[duration['playlist_id']] = duration['total_duration']

        if playlist_id:
            return map[playlist_id] if playlist_id in map else 0

        return map

    def get_all(self, sort: Optional[str] = 'created_at', ascending=False) -> List[Playlist]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, sort=sort, ascending=ascending))

    def get_all_labels_indexed(self) -> Dict:
        index = {}

        for item in self.get_all():
            index[item.id] = item.name

        return index

    def forget_for_user(self, user_id: int):
        playlists = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_playlists = self.user_manager.forget_user_for_entity(playlists, user_id)

        for playlist_id, edits in edits_playlists.items():
            self._db.update_by_id(self.TABLE_NAME, playlist_id, edits)

    def get_available_slug(self, slug) -> str:
        known_playlist = {"slug": slug}
        next_slug = slug
        while known_playlist is not None:
            next_slug = slugify_next(next_slug)
            known_playlist = self.get_one_by(query="slug = ?", values={"slug": next_slug}, sort="created_at", ascending=False, limit=1)

        return next_slug

    def slugify(self, playlist: Dict) -> Dict:
        playlist["slug"] = slugify(playlist["name"])

        known_playlist = self.get_one_by(query="slug = ?", values={
            "slug": playlist["slug"]
        }, sort="created_at", ascending=False, limit=1)

        if known_playlist:
            playlist["slug"] = self.get_available_slug(playlist["slug"])

        return playlist

    def pre_add(self, playlist: Dict) -> Dict:
        playlist = self.slugify(playlist)
        self.user_manager.track_user_on_create(playlist)
        self.user_manager.track_user_on_update(playlist)
        return playlist

    def pre_update(self, playlist: Dict) -> Dict:
        playlist = self.slugify(playlist)
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

    def update_form(self, id: int, name: str, time_sync: bool, enabled: bool) -> None:
        playlist = self.get(id)

        if not playlist:
            return

        form = {
            "name": name,
            "time_sync": time_sync,
            "enabled": enabled
        }

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))

        if playlist.fallback and not enabled:
            self.set_fallback()

        self.post_update(id)

    def check_and_set_fallback(self):
        if len(self.get_by("fallback = 1")) == 0:
            self.set_fallback()

    def set_fallback(self, playlist_id: Optional[int] = 0) -> None:
        self._db.execute_write_query(query="UPDATE {} set fallback = 0".format(self.TABLE_NAME))

        if playlist_id == 0:
            self._db.execute_write_query(query="UPDATE {} set fallback = 1 WHERE id = (select id from {} where enabled = 1 order by created_at DESC LIMIT 1)".format(self.TABLE_NAME, self.TABLE_NAME))
        else:
            self._db.execute_write_query(query="UPDATE {} set fallback = 1 WHERE id = ?".format(self.TABLE_NAME), params=(playlist_id,))

    def add_form(self, playlist: Union[Playlist, Dict]) -> Playlist:
        form = playlist

        if not isinstance(playlist, dict):
            form = playlist.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        playlist = self.get_one_by(query="slug = ?", values={
            "slug": form["slug"]
        })
        self.post_add(playlist.id)
        return playlist

    def delete(self, id: int) -> None:
        playlist = self.get(id)

        if playlist:
            self.pre_delete(id)
            self._db.delete_by_id(self.TABLE_NAME, id)

            if playlist.fallback:
                self.set_fallback()

            self.post_delete(id)

    def to_dict(self, playlists: List[Playlist]) -> List[Dict]:
        return [playlist.to_dict() for playlist in playlists]


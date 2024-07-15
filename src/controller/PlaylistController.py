import json

from flask import Flask, render_template, redirect, request, url_for, jsonify, abort
from src.exceptions.PlaylistSlugAlreadyExist import PlaylistSlugAlreadyExist
from src.service.ModelStore import ModelStore
from src.model.entity.Playlist import Playlist
from src.model.enum.FolderEntity import FolderEntity
from src.model.enum.ContentType import ContentType
from src.interface.ObController import ObController


class PlaylistController(ObController):

    def guard_playlist(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('playlist_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/playlist', 'playlist', self.guard_playlist(self._auth(self.playlist)), methods=['GET'])
        self._app.add_url_rule('/playlist/list/<playlist_id>', 'playlist_list', self.guard_playlist(self._auth(self.playlist_list)), methods=['GET'])
        self._app.add_url_rule('/playlist/add', 'playlist_add', self.guard_playlist(self._auth(self.playlist_add)), methods=['POST'])
        self._app.add_url_rule('/playlist/save', 'playlist_save', self.guard_playlist(self._auth(self.playlist_save)), methods=['POST'])
        self._app.add_url_rule('/playlist/delete/<playlist_id>', 'playlist_delete', self.guard_playlist(self._auth(self.playlist_delete)), methods=['GET'])

    def playlist(self):
        return redirect(url_for('playlist_list', playlist_id=0))

    def playlist_list(self, playlist_id: int = 0):
        current_playlist = self._model_store.playlist().get(playlist_id)
        playlists = self._model_store.playlist().get_all(sort="created_at", ascending=False)
        durations = self._model_store.playlist().get_durations_by_playlists()
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_content').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        if not current_playlist and len(playlists) > 0:
            current_playlist = playlists[0]

        return render_template(
            'playlist/list.jinja.html',
            error=request.args.get('error', None),
            current_playlist=current_playlist,
            playlists=playlists,
            durations=durations,
            slides=self._model_store.slide().get_slides(playlist_id=current_playlist.id),
            foldered_contents=self._model_store.content().get_all_indexed('folder_id', multiple=True),
            contents={content.id: {"id": content.id, "name": content.name, "type": content.type.value} for content in self._model_store.content().get_contents()},
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            folders_tree=self._model_store.folder().get_folder_tree(FolderEntity.CONTENT),
            enum_content_type=ContentType,
            enum_folder_entity=FolderEntity,
        )

    def playlist_add(self):
        playlist = Playlist(
            name=request.form['name'],
            enabled=True,
            time_sync=False
        )

        try:
            playlist = self._model_store.playlist().add_form(playlist)
        except PlaylistSlugAlreadyExist as e:
            abort(409)

        return redirect(url_for('playlist_list', playlist_id=playlist.id))

    def playlist_save(self):
        self._model_store.playlist().update_form(
            id=request.form['id'],
            name=request.form['name'],
            time_sync=True if 'time_sync' in request.form else False,
            enabled=True if 'enabled' in request.form else False
        )
        return redirect(url_for('playlist_list', playlist_id=request.form['id']))

    def playlist_delete(self, playlist_id: int):
        if self._model_store.slide().count_slides_for_playlist(playlist_id) > 0:
            return redirect(url_for('playlist_list', playlist_id=playlist_id, error='playlist_delete_has_slides'))

        if self._model_store.node_player_group().count_node_player_groups_for_playlist(playlist_id) > 0:
            return redirect(url_for('playlist_list', playlist_id=playlist_id, error='playlist_delete_has_node_player_groups'))

        self._model_store.playlist().delete(playlist_id)
        return redirect(url_for('playlist'))

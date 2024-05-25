import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.Playlist import Playlist
from src.interface.ObController import ObController


class PlaylistController(ObController):

    def guard_playlist(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('playlist_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/playlist/list', 'playlist_list', self.guard_playlist(self._auth(self.playlist_list)), methods=['GET'])
        self._app.add_url_rule('/playlist/add', 'playlist_add', self.guard_playlist(self._auth(self.playlist_add)), methods=['POST'])
        self._app.add_url_rule('/playlist/edit', 'playlist_edit', self.guard_playlist(self._auth(self.playlist_edit)), methods=['POST'])
        self._app.add_url_rule('/playlist/toggle', 'playlist_toggle', self.guard_playlist(self._auth(self.playlist_toggle)), methods=['POST'])
        self._app.add_url_rule('/playlist/delete', 'playlist_delete', self.guard_playlist(self._auth(self.playlist_delete)), methods=['DELETE'])

    def playlist(self):
        return render_template(
            'playlist/playlist.jinja.html',
            playlists=self._model_store.playlist().get_enabled_playlists(),
        )

    def playlist_list(self):
        durations = self._model_store.playlist().get_durations_by_playlists()
        return render_template(
            'playlist/list.jinja.html',
            enabled_playlists=self._model_store.playlist().get_enabled_playlists(with_default=True),
            disabled_playlists=self._model_store.playlist().get_disabled_playlists(),
            durations=durations
        )

    def playlist_add(self):
        playlist = Playlist(
            name=request.form['name'],
            time_sync=request.form['time_sync'],
        )

        self._model_store.playlist().add_form(playlist)

        return redirect(url_for('playlist_list'))

    def playlist_edit(self):
        self._model_store.playlist().update_form(
            id=request.form['id'],
            name=request.form['name'],
            time_sync=request.form['time_sync'],
        )
        return redirect(url_for('playlist_list'))

    def playlist_toggle(self):
        data = request.get_json()
        self._model_store.playlist().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def playlist_delete(self):
        data = request.get_json()
        id = data.get('id')
        if self._model_store.slide().count_slides_for_playlist(id) > 0:
            return jsonify({'status': 'error', 'message': self.t('playlist_delete_has_slides')}), 400
        self._model_store.playlist().delete(id)
        return jsonify({'status': 'ok'})

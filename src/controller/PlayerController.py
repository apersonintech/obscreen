import json

from typing import Optional
from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort

from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.util.utils import get_safe_cron_descriptor
from src.util.UtilNetwork import get_ip_address, host_to_safe_ipaddr
from src.model.enum.AnimationSpeed import animation_speed_duration


class PlayerController(ObController):

    def _get_playlist(self, playlist_id: Optional[int] = 0) -> dict:
        enabled_slides = self._model_store.slide().get_slides(enabled=True, playlist_id=playlist_id)
        slides = self._model_store.slide().to_dict(enabled_slides)
        playlist = self._model_store.playlist().get(playlist_id)

        playlist_loop = []
        playlist_cron = []

        for slide in slides:
            if 'cron_schedule' in slide and slide['cron_schedule']:
                if get_safe_cron_descriptor(slide['cron_schedule']):
                    playlist_cron.append(slide)
            else:
                playlist_loop.append(slide)

        playlists = {
            'playlist_id': playlist.id if playlist else None,
            'time_sync': playlist.time_sync if playlist else self._model_store.variable().get_one_by_name("playlist_default_time_sync").as_bool(),
            'loop': playlist_loop,
            'cron': playlist_cron,
            'hard_refresh_request': self._model_store.variable().get_one_by_name("refresh_player_request").as_int()
        }

        return playlists

    def register(self):
        self._app.add_url_rule('/', 'player', self.player, methods=['GET'])
        self._app.add_url_rule('/use/<playlist_slug_or_id>', 'player_use', self.player, methods=['GET'])
        self._app.add_url_rule('/player/default', 'player_default', self.player_default, methods=['GET'])
        self._app.add_url_rule('/player/playlist', 'player_playlist', self.player_playlist, methods=['GET'])
        self._app.add_url_rule('/player/playlist/use/<playlist_slug_or_id>', 'player_playlist_use', self.player_playlist, methods=['GET'])

    def player(self, playlist_slug_or_id: str = ''):
        playlist_slug_or_id = self._get_dynamic_playlist_id(playlist_slug_or_id)

        current_playlist = self._model_store.playlist().get_one_by("slug = ? OR id = ?", {
            "slug": playlist_slug_or_id,
            "id": playlist_slug_or_id
        })

        if playlist_slug_or_id and not current_playlist:
            return abort(404)

        playlist_id = current_playlist.id if current_playlist else None

        return render_template(
            'player/player.jinja.html',
            items=json.dumps(self._get_playlist(playlist_id=playlist_id)),
            default_slide_duration=self._model_store.variable().get_one_by_name('default_slide_duration'),
            polling_interval=self._model_store.variable().get_one_by_name('polling_interval'),
            slide_animation_enabled=self._model_store.variable().get_one_by_name('slide_animation_enabled'),
            slide_animation_entrance_effect=self._model_store.variable().get_one_by_name('slide_animation_entrance_effect'),
            slide_animation_exit_effect=self._model_store.variable().get_one_by_name('slide_animation_exit_effect'),
            slide_animation_speed=self._model_store.variable().get_one_by_name('slide_animation_speed'),
            animation_speed_duration=animation_speed_duration
        )

    def player_default(self):
        return render_template(
            'player/default.jinja.html',
            ipaddr=get_ip_address(),
            time_with_seconds=self._model_store.variable().get_one_by_name('default_slide_time_with_seconds')
        )

    def player_playlist(self, playlist_slug_or_id: str = ''):
        playlist_slug_or_id = self._get_dynamic_playlist_id(playlist_slug_or_id)

        current_playlist = self._model_store.playlist().get_one_by("slug = ? OR id = ?", {
            "slug": playlist_slug_or_id,
            "id": playlist_slug_or_id
        })
        playlist_id = current_playlist.id if current_playlist else None

        return jsonify(self._get_playlist(playlist_id=playlist_id))

    def _get_dynamic_playlist_id(self, playlist_slug_or_id: Optional[str]) -> str:
        if not playlist_slug_or_id and self._model_store.variable().get_one_by_name('fleet_player_enabled'):
            node_player = self._model_store.node_player().get_one_by("host = '{}' and enabled = {}".format(
                host_to_safe_ipaddr(request.headers.getlist("Host")[0]),
                True
            ))

            if node_player and node_player.group_id:
                node_player_group = self._model_store.node_player_group().get(node_player.group_id)
                playlist_slug_or_id = node_player_group.playlist_id
        return playlist_slug_or_id
        
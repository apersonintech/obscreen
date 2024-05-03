import json

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.utils import get_ip_address, get_safe_cron_descriptor


class PlayerController(ObController):

    def _get_playlist(self) -> dict:
        enabled_slides = self._model_store.slide().get_enabled_slides()
        slides = self._model_store.slide().to_dict(enabled_slides)

        playlist_loop = []
        playlist_cron = []

        for slide in slides:
            if 'cron_schedule' in slide and slide['cron_schedule']:
                if get_safe_cron_descriptor(slide['cron_schedule']):
                    playlist_cron.append(slide)
            else:
                playlist_loop.append(slide)

        playlists = {
            'loop': playlist_loop,
            'cron': playlist_cron
        }

        return playlists

    def register(self):
        self._app.add_url_rule('/', 'player', self.player, methods=['GET'])
        self._app.add_url_rule('/player/default', 'player_default', self.player_default, methods=['GET'])
        self._app.add_url_rule('/player/playlist', 'player_playlist', self.player_playlist, methods=['GET'])

    def player(self):
        return render_template(
            'player/player.jinja.html',
            items=json.dumps(self._get_playlist()),
            slide_animation_enabled=self._model_store.variable().get_one_by_name('slide_animation_enabled'),
            slide_animation_entrance_effect=self._model_store.variable().get_one_by_name('slide_animation_entrance_effect'),
            slide_animation_exit_effect=self._model_store.variable().get_one_by_name('slide_animation_exit_effect'),
            slide_animation_speed=self._model_store.variable().get_one_by_name('slide_animation_speed')
        )

    def player_default(self):
        ipaddr = get_ip_address()
        return render_template(
            'player/default.jinja.html',
            ipaddr=ipaddr if ipaddr else self._model_store.lang().map().get('common_unknown_ipaddr'),
            l=self._model_store.lang().map()
        )

    def player_playlist(self):
        return jsonify(self._get_playlist())

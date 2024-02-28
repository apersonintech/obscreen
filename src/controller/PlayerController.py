import json

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from src.utils import get_ip_address


class PlayerController:

    def __init__(self, app, lang_dict, slide_manager):
        self._app = app
        self._lang_dict = lang_dict
        self._slide_manager = slide_manager
        self.register()

    def _get_playlist(self) -> dict:
        slides = self._slide_manager.to_dict(self._slide_manager.get_enabled_slides())

        if len(slides) == 1:
            return [slides[0], slides[0]]

        return slides

    def register(self):
        self._app.add_url_rule('/', 'player', self.player, methods=['GET'])
        self._app.add_url_rule('/player/default', 'player_default', self.player_default, methods=['GET'])
        self._app.add_url_rule('/player/playlist', 'player_playlist', self.player_playlist, methods=['GET'])

    def player(self):
        return render_template(
            'player/player.jinja.html',
            items=json.dumps(self._get_playlist())
        )

    def player_default(self):
        ipaddr = get_ip_address()
        return render_template(
            'player/default.jinja.html',
            ipaddr=ipaddr if ipaddr else self._lang_dict['common_unknown_ipaddr'],
            l=self._lang_dict
        )

    def player_playlist(self):
        return jsonify(self._get_playlist())

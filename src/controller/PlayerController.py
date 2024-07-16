import json
import logging

from datetime import datetime
from typing import Optional
from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort

from src.model.entity.Slide import Slide
from src.exceptions.NoFallbackPlaylistException import NoFallbackPlaylistException
from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.util.utils import get_safe_cron_descriptor, is_valid_cron_date_time, get_cron_date_time
from src.util.UtilNetwork import get_ip_address, get_safe_remote_addr
from src.model.enum.AnimationSpeed import animation_speed_duration


class PlayerController(ObController):

    def register(self):
        self._app.add_url_rule('/', 'player', self.player, methods=['GET'])
        self._app.add_url_rule('/use/<playlist_slug_or_id>', 'player_use', self.player, methods=['GET'])
        self._app.add_url_rule('/player/default', 'player_default', self.player_default, methods=['GET'])
        self._app.add_url_rule('/player/playlist', 'player_playlist', self.player_playlist, methods=['GET'])
        self._app.add_url_rule('/player/playlist/use/<playlist_slug_or_id>', 'player_playlist_use', self.player_playlist, methods=['GET'])

    def player(self, playlist_slug_or_id: str = ''):
        preview_content_id = request.args.get('preview_content_id')
        playlist_slug_or_id = self._get_dynamic_playlist_id(playlist_slug_or_id)

        current_playlist = self._model_store.playlist().get_one_by("slug = ? OR id = ?", {
            "slug": playlist_slug_or_id,
            "id": playlist_slug_or_id
        })

        if playlist_slug_or_id and not current_playlist:
            return abort(404)

        playlist_id = current_playlist.id if current_playlist else None

        try:
            items = self._get_playlist(playlist_id=playlist_id, preview_content_id=preview_content_id)
        except NoFallbackPlaylistException:
            abort(404)

        intro_slide_duration = 0 if items['preview_mode'] else int(request.args.get('intro', self._model_store.variable().get_one_by_name('intro_slide_duration').eval()))
        animation_enabled = bool(request.args.get('animation', int(self._model_store.variable().get_one_by_name('slide_animation_enabled').eval())))
        polling_interval = int(request.args.get('polling', self._model_store.variable().get_one_by_name('polling_interval').eval()))
        slide_animation_speed = request.args.get('animation_speed', self._model_store.variable().get_one_by_name('slide_animation_speed').eval()).lower()
        slide_animation_entrance_effect = request.args.get('animation_effect', self._model_store.variable().get_one_by_name('slide_animation_entrance_effect').eval())
        # slide_animation_exit_effect = request.args.get('slide_animation_exit_effect', self._model_store.variable().get_one_by_name('slide_animation_exit_effect').eval())

        return render_template(
            'player/player.jinja.html',
            items=items,
            intro_slide_duration=intro_slide_duration,
            polling_interval=polling_interval,
            slide_animation_enabled=animation_enabled,
            slide_animation_entrance_effect=slide_animation_entrance_effect,
            slide_animation_speed=slide_animation_speed,
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

        try:
            return jsonify(self._get_playlist(playlist_id=playlist_id))
        except NoFallbackPlaylistException:
            abort(404)

    def _get_dynamic_playlist_id(self, playlist_slug_or_id: Optional[str]) -> str:
        if not playlist_slug_or_id and self._model_store.variable().get_one_by_name('fleet_player_enabled'):
            node_player = self._model_store.node_player().get_one_by("host = '{}'".format(
                get_safe_remote_addr(self.get_remote_addr()),
                True
            ))

            if node_player and node_player.group_id:
                node_player_group = self._model_store.node_player_group().get(node_player.group_id)
                playlist_slug_or_id = node_player_group.playlist_id
        return playlist_slug_or_id

    @staticmethod
    def get_remote_addr() -> str:
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        else:
            return request.remote_addr

    def _get_playlist(self, playlist_id: Optional[int] = 0, preview_content_id: Optional[int] = None) -> dict:
        if playlist_id == 0 or not playlist_id:
            playlist = self._model_store.playlist().get_one_by(query="fallback = 1")

            if playlist:
                playlist_id = playlist.id
            else:
                raise NoFallbackPlaylistException()

        enabled_slides = []
        preview_mode = False

        if preview_content_id:
            content = self._model_store.content().get(preview_content_id)

            if content:
                enabled_slides = [Slide(
                    content_id=content.id,
                    duration=1000000,
                )]
                preview_mode = True
        else:
            enabled_slides = self._model_store.slide().get_slides(enabled=True, playlist_id=playlist_id)

        slides = self._model_store.slide().to_dict(enabled_slides)
        contents = self._model_store.content().get_all_indexed()
        playlist = self._model_store.playlist().get(playlist_id)

        playlist_loop = []
        playlist_notifications = []

        for slide in slides:
            if slide['content_id']:
                if int(slide['content_id']) not in contents:
                    continue

                content = contents[int(slide['content_id'])].to_dict()
                slide['name'] = content['name']
                slide['location'] = content['location']
                slide['type'] = content['type']
            else:
                continue

            has_valid_start_date = 'cron_schedule' in slide and slide['cron_schedule'] and get_safe_cron_descriptor(slide['cron_schedule']) and is_valid_cron_date_time(slide['cron_schedule'])
            has_valid_end_date = 'cron_schedule_end' in slide and slide['cron_schedule_end'] and get_safe_cron_descriptor(slide['cron_schedule_end']) and is_valid_cron_date_time(slide['cron_schedule_end'])

            if slide['is_notification'] and has_valid_start_date:
                if has_valid_start_date:
                    playlist_notifications.append(slide)
                else:
                    logging.warn('Slide {} is notification but start date is invalid'.format(slide['name']))
            else:
                if has_valid_start_date:
                    start_date = get_cron_date_time(slide['cron_schedule'], object=True)
                    if datetime.now() <= start_date:
                        continue

                if has_valid_end_date:
                    end_date = get_cron_date_time(slide['cron_schedule_end'], object=True)
                    if datetime.now() >= end_date:
                        continue

                    playlist_loop.append(slide)
                else:
                    playlist_loop.append(slide)

        playlists = {
            'playlist_id': playlist.id if playlist else None,
            'time_sync': playlist.time_sync if playlist else False,
            'loop': playlist_loop,
            'preview_mode': preview_mode,
            'notifications': playlist_notifications,
            'hard_refresh_request': self._model_store.variable().get_one_by_name("refresh_player_request").as_int()
        }

        return playlists

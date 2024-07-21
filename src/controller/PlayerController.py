import json
import logging
import uuid

from datetime import datetime
from typing import Optional, List, Dict
from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort
from pathlib import Path

from src.model.entity.Slide import Slide
from src.model.enum.ContentType import ContentType
from src.exceptions.NoFallbackPlaylistException import NoFallbackPlaylistException
from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.util.utils import get_safe_cron_descriptor, is_cron_calendar_moment, is_cron_in_day_moment, get_cron_date_time
from src.util.UtilNetwork import get_safe_remote_addr, get_network_interfaces
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
            return redirect(url_for('player_default', noplaylist=1))

        intro_slide_duration = 0 if items['preview_mode'] else int(request.args.get('intro', self._model_store.variable().get_one_by_name('intro_slide_duration').eval()))
        animation_enabled = bool(int(request.args.get('animation', int(self._model_store.variable().get_one_by_name('slide_animation_enabled').eval()))))
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
            interfaces=[iface['ip_address'] for iface in get_network_interfaces()],
            external_url=self._model_store.variable().get_one_by_name('external_url').as_string().strip(),
            time_with_seconds=self._model_store.variable().get_one_by_name('default_slide_time_with_seconds'),
            noplaylist=request.args.get('noplaylist', '0') == '1'
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
                get_safe_remote_addr(self.get_remote_addr_for_node_player()),
                True
            ))

            if node_player and node_player.group_id:
                node_player_group = self._model_store.node_player_group().get(node_player.group_id)
                playlist_slug_or_id = node_player_group.playlist_id
        return playlist_slug_or_id

    @staticmethod
    def get_remote_addr_for_node_player() -> str:
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        else:
            return request.remote_addr

    def _get_playlist(self, playlist_id: Optional[int] = 0, preview_content_id: Optional[int] = None) -> dict:
        preview_content = self._model_store.content().get(preview_content_id) if preview_content_id else None
        preview_mode = preview_content is not None

        if playlist_id == 0 or not playlist_id:
            playlist = self._model_store.playlist().get_one_by(query="fallback = 1")

            if playlist:
                playlist_id = playlist.id
            elif not preview_mode:
                raise NoFallbackPlaylistException()

        enabled_slides = [Slide(content_id=preview_content.id, duration=1000000)] if preview_mode else self._model_store.slide().get_slides(enabled=True, playlist_id=playlist_id)
        slides = self._model_store.slide().to_dict(enabled_slides)
        contents = self._model_store.content().get_all_indexed()
        playlist = self._model_store.playlist().get(playlist_id)
        position = 9999

        playlist_loop = []
        playlist_notifications = []

        for slide in slides:
            if not slide['content_id']:
                continue

            if int(slide['content_id']) not in contents:
                continue

            content = contents[int(slide['content_id'])]
            slide['name'] = content.name
            slide['location'] = content.location
            slide['type'] = content.type.value



            if slide['type'] == ContentType.EXTERNAL_STORAGE.value:
                mount_point_dir = Path(self.get_external_storage_server().get_directory(), slide['location'])
                if mount_point_dir.is_dir():
                    for file in mount_point_dir.iterdir():
                        if file.is_file() and not file.stem.startswith('.'):
                            slide['id'] = str(uuid.uuid4())
                            slide['position'] = position
                            slide['type'] = ContentType.guess_content_type_file(str(file.resolve())).value
                            slide['location'] = "{}/{}".format(
                                self._model_store.content().resolve_content_location(content),
                                file.name
                            )
                            slide['name'] = file.stem
                            logging.info(slide)
                            self._feed_playlist(playlist_loop, playlist_notifications, slide)
                            position = position + 1
            else:
                self._feed_playlist(playlist_loop, playlist_notifications, slide)


        playlists = {
            'playlist_id': playlist.id if playlist else None,
            'time_sync': playlist.time_sync if playlist else False,
            'loop': playlist_loop,
            'preview_mode': preview_mode,
            'notifications': playlist_notifications,
            'hard_refresh_request': self._model_store.variable().get_one_by_name("refresh_player_request").as_int()
        }

        return playlists

    def _feed_playlist(self, loop: List, notifications: List, slide: Dict) -> None:
        has_valid_start_date = 'cron_schedule' in slide and slide['cron_schedule'] and get_safe_cron_descriptor(slide['cron_schedule']) and is_cron_calendar_moment(slide['cron_schedule'])
        has_valid_end_date = 'cron_schedule_end' in slide and slide['cron_schedule_end'] and get_safe_cron_descriptor(slide['cron_schedule_end']) and is_cron_calendar_moment(slide['cron_schedule_end'])

        if slide['is_notification']:
            if has_valid_start_date:
                return notifications.append(slide)
            return logging.warn('Slide \'{}\' is a notification but start date is invalid'.format(slide['name']))

        if has_valid_start_date:
            start_date = get_cron_date_time(slide['cron_schedule'], object=True)
            if datetime.now() <= start_date:
                return

        if has_valid_end_date:
            end_date = get_cron_date_time(slide['cron_schedule_end'], object=True)
            if datetime.now() >= end_date:
                return

        loop.append(slide)

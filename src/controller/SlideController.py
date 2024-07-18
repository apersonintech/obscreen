import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from src.service.ModelStore import ModelStore
from src.model.entity.Slide import Slide
from src.model.enum.ContentType import ContentType
from src.interface.ObController import ObController
from src.util.utils import str_to_enum, get_optional_string
from src.util.UtilFile import randomize_filename


class SlideController(ObController):

    def register(self):
        self._app.add_url_rule('/manage', 'manage', self.manage, methods=['GET'])
        self._app.add_url_rule('/slideshow/slide/add', 'slideshow_slide_add', self._auth(self.slideshow_slide_add), methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/edit', 'slideshow_slide_edit', self._auth(self.slideshow_slide_edit), methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/delete/<slide_id>', 'slideshow_slide_delete', self._auth(self.slideshow_slide_delete), methods=['GET', 'DELETE'])
        self._app.add_url_rule('/slideshow/slide/position', 'slideshow_slide_position', self._auth(self.slideshow_slide_position), methods=['POST'])
        self._app.add_url_rule('/slideshow/player-refresh', 'slideshow_player_refresh', self._auth(self.slideshow_player_refresh), methods=['GET'])

    def manage(self):
        return redirect(url_for('playlist'))

    def slideshow_slide_add(self):
        content = None

        # if 'type' in request.form:
        #     content = self._model_store.content().add_form_raw(
        #         name=request.form['name'],
        #         type=str_to_enum(request.form['type'], ContentType),
        #         request_files=request.files,
        #         upload_dir=self._app.config['UPLOAD_FOLDER'],
        #         location=request.form['object'] if 'object' in request.form else None
        #     )

        if 'content_id' not in request.form or not request.form['content_id']:
            abort(400)

        slide = Slide(
            content_id=content.id if content else request.form['content_id'],
            duration=request.form['duration'],
            enabled='enabled' in request.form and request.form['enabled'],
            is_notification=True if 'is_notification' in request.form else False,
            playlist_id=request.form['playlist_id'] if 'playlist_id' in request.form and request.form['playlist_id'] else None,
            cron_schedule=get_optional_string(request.form['cron_schedule']),
            cron_schedule_end=get_optional_string(request.form['cron_schedule_end']),
        )

        self._model_store.slide().add_form(slide)
        self._post_update()

        if slide.playlist_id:
            return redirect(url_for('playlist_list', playlist_id=slide.playlist_id))

        return redirect(url_for('playlist'))

    def slideshow_slide_edit(self):
        slide = self._model_store.slide().update_form(
            id=request.form['id'],
            content_id=request.form['content_id'],
            enabled='enabled' in request.form and request.form['enabled'],
            duration=request.form['duration'],
            is_notification=True if 'is_notification' in request.form and request.form['is_notification'] == '1' else False,
            cron_schedule=request.form['cron_schedule'],
            cron_schedule_end=request.form['cron_schedule_end'],
        )
        self._post_update()

        if slide.playlist_id:
            return redirect(url_for('playlist_list', playlist_id=slide.playlist_id))

        return redirect(url_for('playlist'))

    def slideshow_slide_delete(self, slide_id: int = 0):
        slide = self._model_store.slide().get(slide_id)

        if not slide:
            abort(404)

        playlist_id = slide.playlist_id

        self._model_store.slide().delete(slide_id)
        duration = self._model_store.playlist().get_durations_by_playlists(playlist_id=playlist_id)

        self._post_update()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'ok', 'duration': duration, 'playlist_id': playlist_id})

        return redirect(url_for('playlist_list', playlist_id=playlist_id))

    def slideshow_slide_position(self):
        data = request.get_json()
        self._model_store.slide().update_positions(data)
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_player_refresh(self):
        self._model_store.variable().update_by_name("refresh_player_request", time.time())
        max_timeout_value = self._model_store.variable().get_one_by_name('polling_interval').as_int()
        query_params = '{}={}'.format('refresh_player', max_timeout_value)
        next_url = request.args.get('next')
        return redirect('{}{}{}'.format(next_url, '&' if '?' in next_url else '?', query_params))

    def _post_update(self):
        self._model_store.variable().update_by_name("last_slide_update", time.time())


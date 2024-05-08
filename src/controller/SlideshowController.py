import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from src.service.ModelStore import ModelStore
from src.model.entity.Slide import Slide
from src.model.enum.SlideType import SlideType
from src.interface.ObController import ObController
from src.utils import str_to_enum, get_optional_string


class SlideshowController(ObController):

    def register(self):
        self._app.add_url_rule('/manage', 'manage', self.manage, methods=['GET'])
        self._app.add_url_rule('/slideshow', 'slideshow_slide_list', self.slideshow, methods=['GET'])
        self._app.add_url_rule('/slideshow/slide/add', 'slideshow_slide_add', self.slideshow_slide_add, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/edit', 'slideshow_slide_edit', self.slideshow_slide_edit, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/toggle', 'slideshow_slide_toggle', self.slideshow_slide_toggle, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/delete', 'slideshow_slide_delete', self.slideshow_slide_delete, methods=['DELETE'])
        self._app.add_url_rule('/slideshow/slide/position', 'slideshow_slide_position', self.slideshow_slide_position, methods=['POST'])
        self._app.add_url_rule('/slideshow/player-refresh', 'slideshow_player_refresh', self.slideshow_player_refresh, methods=['GET'])

    def manage(self):
        return redirect(url_for('slideshow_slide_list'))

    def slideshow(self):
        return render_template(
            'slideshow/list.jinja.html',
            l=self._model_store.lang().map(),
            enabled_slides=self._model_store.slide().get_enabled_slides(),
            disabled_slides=self._model_store.slide().get_disabled_slides(),
            var_last_restart=self._model_store.variable().get_one_by_name('last_restart'),
            var_external_url=self._model_store.variable().get_one_by_name('external_url')
        )

    def slideshow_slide_add(self):
        slide = Slide(
            name=request.form['name'],
            type=str_to_enum(request.form['type'], SlideType),
            duration=request.form['duration'],
            cron_schedule=get_optional_string(request.form['cron_schedule']),
        )

        if slide.has_file():
            if 'object' not in request.files:
                return redirect(request.url)

            object = request.files['object']

            if object.filename == '':
                return redirect(request.url)

            if object:
                object_name = secure_filename(object.filename)
                object_path = os.path.join(self._app.config['UPLOAD_FOLDER'], object_name)
                object.save(object_path)
                slide.location = object_path
        else:
            slide.location = request.form['object']

        self._model_store.slide().add_form(slide)
        self._post_update()

        return redirect(url_for('slideshow_slide_list'))

    def slideshow_slide_edit(self):
        self._model_store.slide().update_form(request.form['id'], request.form['name'], request.form['duration'], request.form['cron_schedule'])
        self._post_update()
        return redirect(url_for('slideshow_slide_list'))

    def slideshow_slide_toggle(self):
        data = request.get_json()
        self._model_store.slide().update_enabled(data.get('id'), data.get('enabled'))
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_slide_delete(self):
        data = request.get_json()
        self._model_store.slide().delete(data.get('id'))
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_slide_position(self):
        data = request.get_json()
        self._model_store.slide().update_positions(data)
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_player_refresh(self):
        self._model_store.variable().update_by_name("refresh_player_request", time.time())
        return redirect(
            url_for(
                'slideshow_slide_list',
                refresh_player=self._model_store.variable().get_one_by_name('polling_interval').as_int()
            )
        )

    def _post_update(self):
        self._model_store.variable().update_by_name("last_slide_update", time.time())


import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from src.service.ModelStore import ModelStore
from src.model.entity.Content import Content
from src.model.enum.ContentType import ContentType
from src.interface.ObController import ObController
from src.util.utils import str_to_enum, get_optional_string
from src.util.UtilFile import randomize_filename


class ContentController(ObController):

    def register(self):
        self._app.add_url_rule('/slideshow/content', 'slideshow_content_list', self._auth(self.slideshow_content_list), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/add', 'slideshow_content_add', self._auth(self.slideshow_content_add), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/edit', 'slideshow_content_edit', self._auth(self.slideshow_content_edit), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete', 'slideshow_content_delete', self._auth(self.slideshow_content_delete), methods=['DELETE'])
        self._app.add_url_rule('/slideshow/content/show/<content_id>', 'slideshow_content_show', self._auth(self.slideshow_content_show), methods=['GET'])

    def slideshow_content_list(self):
        return render_template(
            'slideshow/contents/list.jinja.html',
            contents=self._model_store.content().get_contents(),
            enum_content_type=ContentType
        )

    def slideshow_content_add(self):
        self._model_store.content().add_form_raw(
            name=request.form['name'],
            type=str_to_enum(request.form['type'], ContentType),
            request_files=request.files,
            upload_dir=self._app.config['UPLOAD_FOLDER'],
            location=request.form['object'] if 'object' in request.form else None
        )

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_edit(self):
        self._model_store.content().update_form(
            id=request.form['id'],
            name=request.form['name'],
            location=request.form['location'] if 'location' in request.form and request.form['location'] else None
        )
        self._post_update()

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_delete(self):
        data = request.get_json()
        self._model_store.content().delete(data.get('id'))
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_content_show(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return abort(404)

        var_external_url = self._model_store.variable().get_one_by_name('external_url')
        location = content.location

        if len(var_external_url.as_string().strip()) > 0 and content.has_file():
            location = "{}/{}".format(var_external_url.value, content.location)
        elif content.has_file():
            location = "/{}".format(content.location)

        if content.type == ContentType.YOUTUBE:
            location = "https://www.youtube.com/watch?v={}".format(content.location)

        return redirect(location)

    def _post_update(self):
        pass


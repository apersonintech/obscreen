import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from src.service.ModelStore import ModelStore
from src.model.entity.Content import Content
from src.model.entity.Folder import Folder
from src.model.enum.ContentType import ContentType
from src.model.enum.FolderEntity import FolderEntity, FOLDER_ROOT_PATH
from src.interface.ObController import ObController
from src.util.utils import str_to_enum, get_optional_string
from src.util.UtilFile import randomize_filename


class ContentController(ObController):

    def register(self):
        self._app.add_url_rule('/slideshow/content', 'slideshow_content_list', self._auth(self.slideshow_content_list), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/add-folder', 'slideshow_content_folder_add', self._auth(self.slideshow_content_folder_add), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/move-folder', 'slideshow_content_folder_move', self._auth(self.slideshow_content_folder_move), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/rename-folder', 'slideshow_content_folder_rename', self._auth(self.slideshow_content_folder_rename), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete-folder', 'slideshow_content_folder_delete', self._auth(self.slideshow_content_folder_delete), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/add', 'slideshow_content_add', self._auth(self.slideshow_content_add), methods=['GET', 'POST'])
        self._app.add_url_rule('/slideshow/content/edit/<content_id>', 'slideshow_content_edit', self._auth(self.slideshow_content_edit), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/save/<content_id>', 'slideshow_content_save', self._auth(self.slideshow_content_save), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete', 'slideshow_content_delete', self._auth(self.slideshow_content_delete), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/show/<content_id>', 'slideshow_content_show', self._auth(self.slideshow_content_show), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/cd', 'slideshow_content_cd', self._auth(self.slideshow_content_cd), methods=['GET'])

    def slideshow_content_list(self):
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_content').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        return render_template(
            'slideshow/contents/list.jinja.html',
            contents=self._model_store.content().get_all_indexed('folder_id', multiple=True),
            folders_tree=self._model_store.folder().get_folder_tree(FolderEntity.CONTENT),
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            working_folder_children=self._model_store.folder().get_children(working_folder),
            enum_content_type=ContentType,
            enum_folder_entity=FolderEntity,
        )

    def slideshow_content_folder_add(self):
        self._model_store.folder().add_folder(
            entity=FolderEntity.CONTENT,
            name=request.form['name'],
        )

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_folder_rename(self):
        self._model_store.folder().rename_folder(
            folder_id=request.form['id'],
            name=request.form['name'],
        )

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_folder_move(self):
        self._model_store.folder().move_to_folder(
            entity_id=request.form['entity_id'],
            folder_id=request.form['new_folder_id'],
            entity_is_folder=True if request.form['is_folder'] == '1' else False,
        )

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_folder_delete(self):
        folder = self._model_store.folder().get(request.args.get('id'))

        if not folder:
            return redirect(url_for('slideshow_content_list'))

        content_counter = self._model_store.content().count_contents_for_folder(folder.id)
        folder_counter = self._model_store.folder().count_subfolders_for_folder(folder.id)

        if content_counter > 0 or folder_counter:
            return redirect(url_for('slideshow_content_list', folder_not_empty_error=True))

        self._model_store.folder().delete(id=folder.id)

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_add(self):
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_content').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        self._model_store.content().add_form_raw(
            name=request.form['name'],
            type=str_to_enum(request.form['type'], ContentType),
            request_files=request.files,
            upload_dir=self._app.config['UPLOAD_FOLDER'],
            location=request.form['object'] if 'object' in request.form else None,
            folder_id=working_folder.id if working_folder else None
        )

        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_edit(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return abort(404)

        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_content').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        return render_template(
            'slideshow/contents/edit.jinja.html',
            content=content,
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            working_folder_children=self._model_store.folder().get_children(working_folder),
            enum_content_type=ContentType,
        )

    def slideshow_content_save(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return redirect(url_for('slideshow_content_list'))

        self._model_store.content().update_form(
            id=content.id,
            name=request.form['name'],
            location=request.form['location'] if 'location' in request.form and request.form['location'] else None
        )
        self._post_update()

        return redirect(url_for('slideshow_content_edit', content_id=content_id, saved=1))

    def slideshow_content_delete(self):
        content = self._model_store.content().get(request.args.get('id'))

        if not content:
            return redirect(url_for('slideshow_content_list'))

        slide_counter = self._model_store.slide().count_slides_for_content(content.id)

        if slide_counter > 0:
            return redirect(url_for('slideshow_content_list', referenced_in_slide_error=True))

        self._model_store.content().delete(content.id)
        self._post_update()
        return redirect(url_for('slideshow_content_list'))

    def slideshow_content_cd(self):
        path = request.args.get('path')

        if path == FOLDER_ROOT_PATH:
            self._model_store.variable().update_by_name("last_folder_content", FOLDER_ROOT_PATH)
            return redirect(url_for('slideshow_content_list', path=FOLDER_ROOT_PATH))

        if not path:
            return abort(404)

        cd_folder = self._model_store.folder().get_one_by_path(
            path=path,
            entity=FolderEntity.CONTENT
        )

        if not cd_folder:
            return abort(404)

        self._model_store.variable().update_by_name("last_folder_content", path)

        return redirect(url_for('slideshow_content_list', path=path))

    def slideshow_content_show(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return abort(404)

        var_external_url = self._model_store.variable().get_one_by_name('external_url')
        location = content.location

        if content.type == ContentType.YOUTUBE:
            location = "https://www.youtube.com/watch?v={}".format(content.location)
        elif len(var_external_url.as_string().strip()) > 0 and content.has_file():
            location = "{}/{}".format(var_external_url.value, content.location)
        elif content.has_file():
            location = "/{}".format(content.location)
        elif content.type == ContentType.URL:
            location = 'http://' + content.location if not content.location.startswith('http') else content.location

        return redirect(location)

    def _post_update(self):
        pass


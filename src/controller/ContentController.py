import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from src.service.ModelStore import ModelStore
from src.model.entity.Content import Content
from src.model.enum.ContentType import ContentType
from src.model.enum.FolderEntity import FolderEntity, FOLDER_ROOT_PATH
from src.interface.ObController import ObController
from src.service.ExternalStorageServer import ExternalStorageServer
from src.util.utils import str_to_enum, get_optional_string
from src.util.UtilFile import randomize_filename


class ContentController(ObController):

    def register(self):
        self._app.add_url_rule('/slideshow/content', 'slideshow_content_list', self._auth(self.slideshow_content_list), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/add', 'slideshow_content_add', self._auth(self.slideshow_content_add), methods=['GET', 'POST'])
        self._app.add_url_rule('/slideshow/content/edit/<content_id>', 'slideshow_content_edit', self._auth(self.slideshow_content_edit), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/save/<content_id>', 'slideshow_content_save', self._auth(self.slideshow_content_save), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete', 'slideshow_content_delete', self._auth(self.slideshow_content_delete), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/rename', 'slideshow_content_rename', self._auth(self.slideshow_content_rename), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/cd', 'slideshow_content_cd', self._auth(self.slideshow_content_cd), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/add-folder', 'slideshow_content_folder_add', self._auth(self.slideshow_content_folder_add), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/move-folder', 'slideshow_content_folder_move', self._auth(self.slideshow_content_folder_move), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/rename-folder', 'slideshow_content_folder_rename', self._auth(self.slideshow_content_folder_rename), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete-folder', 'slideshow_content_folder_delete', self._auth(self.slideshow_content_folder_delete), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/show/<content_id>', 'slideshow_content_show', self._auth(self.slideshow_content_show), methods=['GET'])
        self._app.add_url_rule('/slideshow/content/upload-bulk', 'slideshow_content_upload_bulk', self._auth(self.slideshow_content_upload_bulk), methods=['POST'])
        self._app.add_url_rule('/slideshow/content/delete-bulk-explr', 'slideshow_content_delete_bulk_explr', self._auth(self.slideshow_content_delete_bulk_explr), methods=['GET'])

    def get_working_folder(self):
        working_folder_path = request.args.get('path', None)
        working_folder = None

        if working_folder_path:
            working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        if not working_folder:
            working_folder_path = self._model_store.variable().get_one_by_name('last_folder_content').as_string()
            working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.CONTENT)

        return working_folder_path, working_folder

    def slideshow_content_list(self):
        self._model_store.variable().update_by_name('last_pillmenu_slideshow', 'slideshow_content_list')
        working_folder_path, working_folder = self.get_working_folder()
        slides_with_content = self._model_store.slide().get_all_indexed(attribute='content_id', multiple=True)

        return render_template(
            'slideshow/contents/list.jinja.html',
            foldered_contents=self._model_store.content().get_all_indexed('folder_id', multiple=True),
            folders_tree=self._model_store.folder().get_folder_tree(FolderEntity.CONTENT),
            slides_with_content=slides_with_content,
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            working_folder_children=self._model_store.folder().get_children(folder=working_folder, entity=FolderEntity.CONTENT, sort='created_at', ascending=False),
            enum_content_type=ContentType,
            enum_folder_entity=FolderEntity
        )

    def slideshow_content_add(self):
        working_folder_path, working_folder = self.get_working_folder()
        route_args = {
            "path": working_folder_path,
        }

        location = request.form['object'] if 'object' in request.form else None

        content = self._model_store.content().add_form_raw(
            name=request.form['name'],
            type=str_to_enum(request.form['type'], ContentType),
            request_files=request.files,
            upload_dir=self._app.config['UPLOAD_FOLDER'],
            location=location,
            folder_id=working_folder.id if working_folder else None
        )

        if not content:
            route_args["error"] = 'common_bad_file_type'

        return redirect(url_for('slideshow_content_list', **route_args))

    def slideshow_content_upload_bulk(self):
        working_folder_path, working_folder = self.get_working_folder()

        for key in request.files:
            files = request.files.getlist(key)
            for file in files:
                type = ContentType.guess_content_type_file(file.filename)
                name = file.filename.rsplit('.', 1)[0]

                if type:
                    self._model_store.content().add_form_raw(
                        name=name,
                        type=type,
                        request_files=file,
                        upload_dir=self._app.config['UPLOAD_FOLDER'],
                        folder_id=working_folder.id if working_folder else None
                    )

        return redirect(url_for('slideshow_content_list', path=working_folder_path))

    def slideshow_content_edit(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return abort(404)

        working_folder_path, working_folder = self.get_working_folder()

        return render_template(
            'slideshow/contents/edit.jinja.html',
            content=content,
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            enum_content_type=ContentType,
        )

    def slideshow_content_save(self, content_id: int = 0):
        working_folder_path, working_folder = self.get_working_folder()
        content = self._model_store.content().get(content_id)

        if not content:
            return redirect(url_for('slideshow_content_list', path=working_folder_path))

        self._model_store.content().update_form(
            id=content.id,
            name=request.form['name'],
            location=request.form['location'] if 'location' in request.form and request.form['location'] else None
        )
        self._post_update()

        return redirect(url_for('slideshow_content_edit', content_id=content_id, saved=1))

    def slideshow_content_delete(self):
        working_folder_path, working_folder = self.get_working_folder()
        error_tuple = self.delete_content_by_id(request.args.get('id'))
        route_args = {
            "path": working_folder_path,
        }

        if error_tuple:
            route_args[error_tuple[0]] = error_tuple[1]

        return redirect(url_for('slideshow_content_list', **route_args))

    def slideshow_content_rename(self):
        working_folder_path, working_folder = self.get_working_folder()
        self._model_store.content().update_form(
            id=request.form['id'],
            name=request.form['name'],
        )

        return redirect(url_for('slideshow_content_list', path=working_folder_path))

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

    def slideshow_content_folder_add(self):
        working_folder_path, working_folder = self.get_working_folder()

        self._model_store.folder().add_folder(
            entity=FolderEntity.CONTENT,
            name=request.form['name'],
            working_folder_path=working_folder_path
        )

        return redirect(url_for('slideshow_content_list', path=working_folder_path))

    def slideshow_content_folder_rename(self):
        working_folder_path, working_folder = self.get_working_folder()
        self._model_store.folder().rename_folder(
            folder_id=request.form['id'],
            name=request.form['name'],
        )

        return redirect(url_for('slideshow_content_list', path=working_folder_path))

    def slideshow_content_folder_move(self):
        working_folder_path, working_folder = self.get_working_folder()
        entity_ids = request.form['entity_ids'].split(',')
        folder_ids = request.form['folder_ids'].split(',')

        for id in entity_ids:
            self._model_store.folder().move_to_folder(
                entity_id=id,
                folder_id=request.form['new_folder_id'],
                entity_is_folder=False,
                entity=FolderEntity.CONTENT
            )

        for id in folder_ids:
            self._model_store.folder().move_to_folder(
                entity_id=id,
                folder_id=request.form['new_folder_id'],
                entity_is_folder=True,
                entity=FolderEntity.CONTENT
            )

        return redirect(url_for('slideshow_content_list', path=working_folder_path))

    def slideshow_content_folder_delete(self):
        working_folder_path, working_folder = self.get_working_folder()
        error_tuple = self.delete_folder_by_id(request.args.get('id'))
        route_args = {
            "path": working_folder_path,
        }

        if error_tuple:
            route_args[error_tuple[0]] = error_tuple[1]

        return redirect(url_for('slideshow_content_list', **route_args))

    def slideshow_content_show(self, content_id: int = 0):
        content = self._model_store.content().get(content_id)

        if not content:
            return abort(404)

        return redirect(self._model_store.content().resolve_content_location(content))

    def slideshow_content_delete_bulk_explr(self):
        working_folder_path, working_folder = self.get_working_folder()
        entity_ids = request.args.get('entity_ids', '').split(',')
        folder_ids = request.args.get('folder_ids', '').split(',')
        route_args_dict = {"path": working_folder_path}

        for id in entity_ids:
            if id:
                error_tuple = self.delete_content_by_id(id)

                if error_tuple:
                    route_args_dict[error_tuple[0]] = error_tuple[1]

        for id in folder_ids:
            if id:
                error_tuple = self.delete_folder_by_id(id)

                if error_tuple:
                    route_args_dict[error_tuple[0]] = error_tuple[1]

        return redirect(url_for('slideshow_content_list', **route_args_dict))

    def delete_content_by_id(self, id):
        content = self._model_store.content().get(id)

        if not content:
            return None

        if self._model_store.slide().count_slides_for_content(content.id) > 0:
            return 'referenced_in_slide_error', content.name

        self._model_store.content().delete(content.id)
        self._post_update()
        return None

    def delete_folder_by_id(self, id):
        folder = self._model_store.folder().get(id)

        if not folder:
            return None

        content_counter = self._model_store.content().count_contents_for_folder(folder.id)
        folder_counter = self._model_store.folder().count_subfolders_for_folder(folder.id)

        if content_counter > 0 or folder_counter:
            return 'folder_not_empty_error', folder.name

        self._model_store.folder().delete(id=folder.id)
        self._post_update()
        return None

    def _post_update(self):
        pass


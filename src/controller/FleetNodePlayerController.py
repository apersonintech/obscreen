import json

from flask import Flask, render_template, redirect, request, url_for, jsonify, abort
from src.service.ModelStore import ModelStore
from src.model.entity.NodePlayer import NodePlayer
from src.interface.ObController import ObController
from src.model.enum.OperatingSystem import OperatingSystem
from src.model.enum.FolderEntity import FolderEntity, FOLDER_ROOT_PATH
from src.util.utils import str_to_enum


class FleetNodePlayerController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_player_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet/node-player', 'fleet_node_player_list', self.guard_fleet(self._auth(self.fleet_node_player_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player/add', 'fleet_node_player_add', self.guard_fleet(self._auth(self.fleet_node_player_add)), methods=['GET', 'POST'])
        self._app.add_url_rule('/fleet/node-player/edit/<node_player_id>', 'fleet_node_player_edit', self._auth(self.fleet_node_player_edit), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player/save/<node_player_id>', 'fleet_node_player_save', self._auth(self.fleet_node_player_save), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/delete', 'fleet_node_player_delete', self.guard_fleet(self._auth(self.fleet_node_player_delete)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player/cd', 'fleet_node_player_cd', self._auth(self.fleet_node_player_cd), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player/add-folder', 'fleet_node_player_folder_add', self._auth(self.fleet_node_player_folder_add), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/move-folder', 'fleet_node_player_folder_move', self._auth(self.fleet_node_player_folder_move), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/rename-folder', 'fleet_node_player_folder_rename', self._auth(self.fleet_node_player_folder_rename), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/delete-folder', 'fleet_node_player_folder_delete', self._auth(self.fleet_node_player_folder_delete), methods=['GET'])

    def fleet_node_player_list(self):
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_node_player').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.NODE_PLAYER)
        return render_template(
            'fleet/node-players/list.jinja.html',
            node_players=self._model_store.node_player().get_all_indexed('folder_id', multiple=True),
            folders_tree=self._model_store.folder().get_folder_tree(FolderEntity.NODE_PLAYER),
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            working_folder_children=self._model_store.folder().get_children(folder=working_folder, entity=FolderEntity.NODE_PLAYER, sort='created_at', ascending=False),
            enum_operating_system=OperatingSystem,
            enum_folder_entity=FolderEntity,
        )

    def fleet_node_player_add(self):
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_node_player').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.NODE_PLAYER)

        self._model_store.node_player().add_form(
            NodePlayer(
                name=request.form['name'],
                host=request.form['host'],
                operating_system=str_to_enum(request.form['operating_system'], OperatingSystem),
                folder_id=working_folder.id if working_folder else None,
            )
        )

        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_edit(self, node_player_id: int = 0):
        node_player = self._model_store.node_player().get(node_player_id)

        if not node_player:
            return abort(404)

        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_node_player').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.NODE_PLAYER)

        return render_template(
            'fleet/node-players/edit.jinja.html',
            node_player=node_player,
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            enum_operating_system=OperatingSystem,
        )

    def fleet_node_player_save(self, node_player_id: int = 0):
        node_player = self._model_store.node_player().get(node_player_id)

        if not node_player:
            return redirect(url_for('fleet_node_player_list'))

        self._model_store.node_player().update_form(
            id=node_player.id,
            name=request.form['name'],
            operating_system=str_to_enum(request.form['operating_system'], OperatingSystem),
            host=request.form['host'],
        )
        self._post_update()

        return redirect(url_for('fleet_node_player_edit', node_player_id=node_player_id, saved=1))

    def fleet_node_player_delete(self):
        node_player = self._model_store.node_player().get(request.args.get('id'))

        if not node_player:
            return redirect(url_for('fleet_node_player_list'))

        self._model_store.node_player().delete(node_player.id)
        self._post_update()
        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_cd(self):
        path = request.args.get('path')

        if path == FOLDER_ROOT_PATH:
            self._model_store.variable().update_by_name("last_folder_node_player", FOLDER_ROOT_PATH)
            return redirect(url_for('fleet_node_player_list', path=FOLDER_ROOT_PATH))

        if not path:
            return abort(404)

        cd_folder = self._model_store.folder().get_one_by_path(
            path=path,
            entity=FolderEntity.NODE_PLAYER
        )

        if not cd_folder:
            return abort(404)

        self._model_store.variable().update_by_name("last_folder_node_player", path)

        return redirect(url_for('fleet_node_player_list', path=path))

    def fleet_node_player_folder_add(self):
        self._model_store.folder().add_folder(
            entity=FolderEntity.NODE_PLAYER,
            name=request.form['name'],
        )

        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_folder_rename(self):
        self._model_store.folder().rename_folder(
            folder_id=request.form['id'],
            name=request.form['name'],
        )

        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_folder_move(self):
        self._model_store.folder().move_to_folder(
            entity_id=request.form['entity_id'],
            folder_id=request.form['new_folder_id'],
            entity_is_folder=True if request.form['is_folder'] == '1' else False,
        )

        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_folder_delete(self):
        folder = self._model_store.folder().get(request.args.get('id'))

        if not folder:
            return redirect(url_for('fleet_node_player_list'))

        node_player_counter = self._model_store.node_player().count_node_players_for_folder(folder.id)
        folder_counter = self._model_store.folder().count_subfolders_for_folder(folder.id)

        if node_player_counter > 0 or folder_counter:
            return redirect(url_for('fleet_node_player_list', folder_not_empty_error=True))

        self._model_store.folder().delete(id=folder.id)

        return redirect(url_for('fleet_node_player_list'))

    def _post_update(self):
        pass

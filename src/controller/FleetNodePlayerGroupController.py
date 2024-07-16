import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.NodePlayerGroup import NodePlayerGroup
from src.model.enum.FolderEntity import FolderEntity
from src.model.enum.OperatingSystem import OperatingSystem
from src.interface.ObController import ObController


class FleetNodePlayerGroupController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_player_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet/node-player-group', 'fleet_node_player_group', self.guard_fleet(self._auth(self.fleet_node_player_group)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player-group/list/<player_group_id>', 'fleet_node_player_group_list', self.guard_fleet(self._auth(self.fleet_node_player_group_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player-group/add', 'fleet_node_player_group_add', self.guard_fleet(self._auth(self.fleet_node_player_group_add)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player-group/save', 'fleet_node_player_group_save', self.guard_fleet(self._auth(self.fleet_node_player_group_save)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player-group/delete/<player_group_id>', 'fleet_node_player_group_delete', self.guard_fleet(self._auth(self.fleet_node_player_group_delete)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player-group/unassign-player/<player_id>', 'fleet_node_player_group_unassign_player', self._auth(self.fleet_node_player_group_unassign_player), methods=['GET', 'DELETE'])
        self._app.add_url_rule('/fleet/node-player-group/assign-player/<player_group_id>/<player_id>', 'fleet_node_player_group_assign_player', self._auth(self.fleet_node_player_group_assign_player), methods=['GET'])

    def fleet_node_player_group(self):
        return redirect(url_for('fleet_node_player_group_list', player_group_id=0))

    def fleet_node_player_group_list(self, player_group_id: int = 0):
        self._model_store.variable().update_by_name('last_pillmenu_fleet', 'fleet_node_player_group')
        current_player_group = self._model_store.node_player_group().get(player_group_id)
        node_player_groups = self._model_store.node_player_group().get_all(sort="created_at", ascending=False)
        pcounters = self._model_store.node_player_group().get_player_counters_by_player_groups()
        working_folder_path = self._model_store.variable().get_one_by_name('last_folder_node_player').as_string()
        working_folder = self._model_store.folder().get_one_by_path(path=working_folder_path, entity=FolderEntity.NODE_PLAYER)

        if not current_player_group and len(node_player_groups) > 0:
            current_player_group = None

        return render_template(
            'fleet/player-group/list.jinja.html',
            error=request.args.get('error', None),
            current_player_group=current_player_group,
            node_player_groups=node_player_groups,
            pcounters=pcounters,
            playlists=self._model_store.playlist().get_all_labels_indexed(),
            players=[] if not current_player_group else self._model_store.node_player().get_node_players(
                group_id=current_player_group.id,
                sort='created_at',
                ascending=True
            ),
            foldered_node_players=self._model_store.node_player().get_all_indexed('folder_id', multiple=True),
            working_folder_path=working_folder_path,
            working_folder=working_folder,
            folders_tree=self._model_store.folder().get_folder_tree(FolderEntity.NODE_PLAYER),
            enum_operating_system=OperatingSystem,
            enum_folder_entity=FolderEntity,
        )

    def fleet_node_player_group_add(self):
        playlist_id = request.form['playlist_id'] if 'playlist_id' in request.form and request.form['playlist_id'] else None
        node_player_group = NodePlayerGroup(
            name=request.form['name'],
            playlist_id=playlist_id,
        )

        try:
            node_player_group = self._model_store.node_player_group().add_form(node_player_group)
        except:
            abort(409)

        self._model_store.node_player_group().add_form(node_player_group)
        return redirect(url_for('fleet_node_player_group_list', player_group_id=node_player_group.id))

    def fleet_node_player_group_save(self):
        playlist_id = request.form['playlist_id'] if 'playlist_id' in request.form and request.form['playlist_id'] else None
        self._model_store.node_player_group().update_form(
            id=request.form['id'],
            name=request.form['name'],
            playlist_id=playlist_id
        )
        return redirect(url_for('fleet_node_player_group_list', player_group_id=request.form['id']))

    def fleet_node_player_group_delete(self, player_group_id: int):
        if self._model_store.node_player().count_node_players_for_group(player_group_id) > 0:
            return redirect(url_for('fleet_node_player_group_list', player_group_id=player_group_id, error='node_player_group_delete_has_node_player'))

        self._model_store.node_player_group().delete(player_group_id)
        return redirect(url_for('fleet_node_player_group'))

    def fleet_node_player_group_unassign_player(self, player_id: int = 0):
        player_id = request.form['id'] if 'id' in request.form else player_id
        node_player = self._model_store.node_player().get(player_id)

        if not node_player:
            return redirect(url_for('fleet_node_player_group'))

        group_id = node_player.group_id

        self._model_store.node_player().update_form(
            id=node_player.id,
            group_id=False,
        )
        self._post_update()
        pcounter = self._model_store.node_player_group().get_player_counters_by_player_groups(group_id=group_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'ok', 'pcounter': pcounter, 'group_id': group_id})

        return redirect(url_for('fleet_node_player_group_list', player_group_id=group_id))

    def fleet_node_player_group_assign_player(self, player_group_id: int = 0, player_id: int = 0):
        node_player_group = self._model_store.node_player_group().get(player_group_id)

        if not node_player_group:
            return redirect(url_for('fleet_node_player_group'))

        node_player = self._model_store.node_player().get(player_id)

        if not node_player:
            return redirect(url_for('fleet_node_player_group_list', player_group_id=node_player_group.id))

        self._model_store.node_player().update_form(
            id=node_player.id,
            group_id=node_player_group.id,
        )
        self._post_update()

        return redirect(url_for('fleet_node_player_group_list', player_group_id=node_player_group.id))

    def _post_update(self):
        pass

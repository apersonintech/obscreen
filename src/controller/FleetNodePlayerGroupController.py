import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.NodePlayerGroup import NodePlayerGroup
from src.interface.ObController import ObController


class FleetNodePlayerGroupController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_player_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet/node-player-group/list', 'fleet_node_player_group_list', self.guard_fleet(self._auth(self.fleet_node_player_group_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player-group/add', 'fleet_node_player_group_add', self.guard_fleet(self._auth(self.fleet_node_player_group_add)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player-group/edit', 'fleet_node_player_group_edit', self.guard_fleet(self._auth(self.fleet_node_player_group_edit)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player-group/delete', 'fleet_node_player_group_delete', self.guard_fleet(self._auth(self.fleet_node_player_group_delete)), methods=['DELETE'])

    def fleet_node_player_group_list(self):
        return render_template(
            'fleet/player-group/list.jinja.html',
            node_player_groups=self._model_store.node_player_group().get_all(),
            playlists=self._model_store.playlist().get_all_labels_indexed()
        )

    def fleet_node_player_group_add(self):
        playlist_id = request.form['playlist_id'] if 'playlist_id' in request.form and request.form['playlist_id'] else None
        self._model_store.node_player_group().add_form(NodePlayerGroup(
            name=request.form['name'],
            playlist_id=playlist_id,
        ))
        return redirect(url_for('fleet_node_player_group_list'))

    def fleet_node_player_group_edit(self):
        playlist_id = request.form['playlist_id'] if 'playlist_id' in request.form and request.form['playlist_id'] else None
        self._model_store.node_player_group().update_form(request.form['id'], request.form['name'], playlist_id)
        return redirect(url_for('fleet_node_player_group_list'))

    def fleet_node_player_group_delete(self):
        data = request.get_json()
        id = data.get('id')

        if self._model_store.node_player().count_node_players_for_group(id) > 0:
            return jsonify({'status': 'error', 'message': self.t('node_player_group_delete_has_node_player')}), 400

        self._model_store.node_player_group().delete(id)
        return jsonify({'status': 'ok'})

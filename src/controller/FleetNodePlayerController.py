import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.NodePlayer import NodePlayer
from src.interface.ObController import ObController


class FleetNodePlayerController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_player_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet/node-player/list', 'fleet_node_player_list', self.guard_fleet(self._auth(self.fleet_node_player_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-player/add', 'fleet_node_player_add', self.guard_fleet(self._auth(self.fleet_node_player_add)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/edit', 'fleet_node_player_edit', self.guard_fleet(self._auth(self.fleet_node_player_edit)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/toggle', 'fleet_node_player_toggle', self.guard_fleet(self._auth(self.fleet_node_player_toggle)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-player/delete', 'fleet_node_player_delete', self.guard_fleet(self._auth(self.fleet_node_player_delete)), methods=['DELETE'])
        self._app.add_url_rule('/fleet/node-player/position', 'fleet_node_player_position', self.guard_fleet(self._auth(self.fleet_node_player_position)), methods=['POST'])

    def fleet_node_player_list(self):
        return render_template(
            'fleet/player/list.jinja.html',
            enabled_node_players=self._model_store.node_player().get_enabled_node_players(),
            disabled_node_players=self._model_store.node_player().get_disabled_node_players(),
        )

    def fleet_node_player_add(self):
        self._model_store.node_player().add_form(NodePlayer(
            name=request.form['name'],
            host=request.form['host'],
        ))
        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_edit(self):
        self._model_store.node_player().update_form(request.form['id'], request.form['name'], request.form['host'])
        return redirect(url_for('fleet_node_player_list'))

    def fleet_node_player_toggle(self):
        data = request.get_json()
        self._model_store.node_player().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def fleet_node_player_delete(self):
        data = request.get_json()
        self._model_store.node_player().delete(data.get('id'))
        return jsonify({'status': 'ok'})

    def fleet_node_player_position(self):
        data = request.get_json()
        self._model_store.node_player().update_positions(data)
        return jsonify({'status': 'ok'})

import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.NodeStudio import NodeStudio
from src.interface.ObController import ObController


class FleetNodeStudioController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_studio_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet', 'fleet', self.guard_fleet(self._auth(self.fleet)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-studio/list', 'fleet_node_studio_list', self.guard_fleet(self._auth(self.fleet_node_studio_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/node-studio/add', 'fleet_node_studio_add', self.guard_fleet(self._auth(self.fleet_node_studio_add)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-studio/edit', 'fleet_node_studio_edit', self.guard_fleet(self._auth(self.fleet_node_studio_edit)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-studio/toggle', 'fleet_node_studio_toggle', self.guard_fleet(self._auth(self.fleet_node_studio_toggle)), methods=['POST'])
        self._app.add_url_rule('/fleet/node-studio/delete', 'fleet_node_studio_delete', self.guard_fleet(self._auth(self.fleet_node_studio_delete)), methods=['DELETE'])
        self._app.add_url_rule('/fleet/node-studio/position', 'fleet_node_studio_position', self.guard_fleet(self._auth(self.fleet_node_studio_position)), methods=['POST'])

    def fleet(self):
        return render_template(
            'fleet/studio/fleet-studio.jinja.html',
            node_studios=self._model_store.node_studio().get_enabled_node_studios(),
        )

    def fleet_node_studio_list(self):
        return render_template(
            'fleet/studio/list.jinja.html',
            enabled_node_studios=self._model_store.node_studio().get_enabled_node_studios(),
            disabled_node_studios=self._model_store.node_studio().get_disabled_node_studios(),
        )

    def fleet_node_studio_add(self):
        self._model_store.node_studio().add_form(NodeStudio(
            name=request.form['name'],
            host=request.form['host'],
            port=request.form['port'],
        ))
        return redirect(url_for('fleet_node_studio_list'))

    def fleet_node_studio_edit(self):
        self._model_store.node_studio().update_form(request.form['id'], request.form['name'], request.form['host'], request.form['port'])
        return redirect(url_for('fleet_node_studio_list'))

    def fleet_node_studio_toggle(self):
        data = request.get_json()
        self._model_store.node_studio().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def fleet_node_studio_delete(self):
        data = request.get_json()
        self._model_store.node_studio().delete(data.get('id'))
        return jsonify({'status': 'ok'})

    def fleet_node_studio_position(self):
        data = request.get_json()
        self._model_store.node_studio().update_positions(data)
        return jsonify({'status': 'ok'})

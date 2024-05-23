import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.Studio import Studio
from src.interface.ObController import ObController


class FleetController(ObController):

    def guard_fleet(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('fleet_studio_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/fleet', 'fleet', self.guard_fleet(self._auth(self.fleet)), methods=['GET'])
        self._app.add_url_rule('/fleet/studio/list', 'fleet_studio_list', self.guard_fleet(self._auth(self.fleet_studio_list)), methods=['GET'])
        self._app.add_url_rule('/fleet/studio/add', 'fleet_studio_add', self.guard_fleet(self._auth(self.fleet_studio_add)), methods=['POST'])
        self._app.add_url_rule('/fleet/studio/edit', 'fleet_studio_edit', self.guard_fleet(self._auth(self.fleet_studio_edit)), methods=['POST'])
        self._app.add_url_rule('/fleet/studio/toggle', 'fleet_studio_toggle', self.guard_fleet(self._auth(self.fleet_studio_toggle)), methods=['POST'])
        self._app.add_url_rule('/fleet/studio/delete', 'fleet_studio_delete', self.guard_fleet(self._auth(self.fleet_studio_delete)), methods=['DELETE'])
        self._app.add_url_rule('/fleet/studio/position', 'fleet_studio_position', self.guard_fleet(self._auth(self.fleet_studio_position)), methods=['POST'])

    def fleet(self):
        return render_template(
            'fleet/fleet.jinja.html',
            studios=self._model_store.studio().get_enabled_studios(),
        )

    def fleet_studio_list(self):
        return render_template(
            'fleet/list.jinja.html',
            enabled_studios=self._model_store.studio().get_enabled_studios(),
            disabled_studios=self._model_store.studio().get_disabled_studios(),
        )

    def fleet_studio_add(self):
        self._model_store.studio().add_form(Studio(
            name=request.form['name'],
            host=request.form['host'],
            port=request.form['port'],
        ))
        return redirect(url_for('fleet_studio_list'))

    def fleet_studio_edit(self):
        self._model_store.studio().update_form(request.form['id'], request.form['name'], request.form['host'], request.form['port'])
        return redirect(url_for('fleet_studio_list'))

    def fleet_studio_toggle(self):
        data = request.get_json()
        self._model_store.studio().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def fleet_studio_delete(self):
        data = request.get_json()
        self._model_store.studio().delete(data.get('id'))
        return jsonify({'status': 'ok'})

    def fleet_studio_position(self):
        data = request.get_json()
        self._model_store.studio().update_positions(data)
        return jsonify({'status': 'ok'})

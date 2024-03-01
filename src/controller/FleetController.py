import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.service.ModelStore import ModelStore
from src.model.entity.Screen import Screen
from src.interface.ObController import ObController


class FleetController(ObController):

    def register(self):
        self._app.add_url_rule('/fleet', 'fleet', self.fleet, methods=['GET'])
        self._app.add_url_rule('/fleet/screen/list', 'fleet_screen_list', self.fleet_screen_list, methods=['GET'])
        self._app.add_url_rule('/fleet/screen/add', 'fleet_screen_add', self.fleet_screen_add, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/edit', 'fleet_screen_edit', self.fleet_screen_edit, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/toggle', 'fleet_screen_toggle', self.fleet_screen_toggle, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/delete', 'fleet_screen_delete', self.fleet_screen_delete, methods=['DELETE'])
        self._app.add_url_rule('/fleet/screen/position', 'fleet_screen_position', self.fleet_screen_position, methods=['POST'])

    def fleet(self):
        return render_template(
            'fleet/fleet.jinja.html',
            screens=self._model_store.screen().get_enabled_screens(),
        )

    def fleet_screen_list(self):
        return render_template(
            'fleet/list.jinja.html',
            l=self._model_store.lang().map(),
            enabled_screens=self._model_store.screen().get_enabled_screens(),
            disabled_screens=self._model_store.screen().get_disabled_screens(),
        )

    def fleet_screen_add(self):
        self._model_store.screen().add_form(Screen(
            name=request.form['name'],
            host=request.form['host'],
            port=request.form['port'],
        ))
        return redirect(url_for('fleet_screen_list'))

    def fleet_screen_edit(self):
        self._model_store.screen().update_form(request.form['id'], request.form['name'], request.form['host'], request.form['port'])
        return redirect(url_for('fleet_screen_list'))

    def fleet_screen_toggle(self):
        data = request.get_json()
        self._model_store.screen().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def fleet_screen_delete(self):
        data = request.get_json()
        self._model_store.screen().delete(data.get('id'))
        return jsonify({'status': 'ok'})

    def fleet_screen_position(self):
        data = request.get_json()
        self._model_store.screen().update_positions(data)
        return jsonify({'status': 'ok'})

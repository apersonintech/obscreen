import time
import json

from flask import Flask, render_template, redirect, request, url_for
from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController


class SettingsController(ObController):

    def register(self):
        self._app.add_url_rule('/settings/variable/list', 'settings_variable_list', self.settings_variable_list, methods=['GET'])
        self._app.add_url_rule('/settings/variable/edit', 'settings_variable_edit', self.settings_variable_edit, methods=['POST'])

    def settings_variable_list(self):
        return render_template(
            'settings/list.jinja.html',
            system_variables=self._model_store.variable().get_editable_variables(plugin=False),
            plugin_variables=self._model_store.variable().get_editable_variables(plugin=True),
        )

    def settings_variable_edit(self):
        self._model_store.variable().update_form(request.form['id'], request.form['value'])
        self._post_update(request.form['id'])
        return redirect(url_for('settings_variable_list'))

    def _post_update(self, id: str):
        variable = self._model_store.variable().get(id)

        if variable.refresh_player:
            self._model_store.variable().update_by_name("refresh_player_request", time.time())


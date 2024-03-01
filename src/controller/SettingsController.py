import json

from flask import Flask, render_template, redirect, request, url_for
from src.service.ModelManager import ModelManager


class SettingsController:

    def __init__(self, app, model_manager: ModelManager):
        self._app = app
        self._model_manager = model_manager
        self.register()

    def register(self):
        self._app.add_url_rule('/settings/variable/list', 'settings_variable_list', self.settings_variable_list, methods=['GET'])
        self._app.add_url_rule('/settings/variable/edit', 'settings_variable_edit', self.settings_variable_edit, methods=['POST'])

    def settings_variable_list(self):
        return render_template(
            'settings/list.jinja.html',
            l=self._model_manager.lang().map(),
            variables=self._model_manager.variable().get_editable_variables(),
        )

    def settings_variable_edit(self):
        self._model_manager.variable().update_form(request.form['id'], request.form['value'])
        return redirect(url_for('settings_variable_list'))
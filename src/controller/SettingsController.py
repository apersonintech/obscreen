import json

from flask import Flask, render_template, redirect, request, url_for


class SettingsController:

    def __init__(self, app, lang_dict, variable_manager):
        self._app = app
        self._lang_dict = lang_dict
        self._variable_manager = variable_manager
        self.register()

    def register(self):
        self._app.add_url_rule('/settings/variable/list', 'settings_variable_list', self.settings_variable_list, methods=['GET'])
        self._app.add_url_rule('/settings/variable/edit', 'settings_variable_edit', self.settings_variable_edit, methods=['POST'])

    def settings_variable_list(self):
        return render_template(
            'settings/list.jinja.html',
            l=self._lang_dict,
            variables=self._variable_manager.get_all(),
        )

    def settings_variable_edit(self):
        self._variable_manager.update_form(request.form['id'], request.form['value'])
        return redirect(url_for('settings_variable_list'))
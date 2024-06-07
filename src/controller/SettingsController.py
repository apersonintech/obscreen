import time
import json

from flask import Flask, render_template, redirect, request, url_for
from typing import Optional

from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.model.entity.User import User


class SettingsController(ObController):

    def register(self):
        self._app.add_url_rule('/settings/variable/list', 'settings_variable_list', self._auth(self.settings_variable_list), methods=['GET'])
        self._app.add_url_rule('/settings/variable/edit', 'settings_variable_edit', self._auth(self.settings_variable_edit), methods=['POST'])

    def settings_variable_list(self):
        return render_template(
            'settings/list.jinja.html',
            plugins=self._model_store.plugins(),
            system_variables=self._model_store.variable().get_editable_variables(plugin=False, sort='section'),
            plugin_variables=self._model_store.variable().get_editable_variables(plugin=True, sort='plugin'),
        )

    def settings_variable_edit(self):
        error = self._pre_update(request.form['id'])

        if error:
            return redirect(url_for('settings_variable_list', error=error))

        self._model_store.variable().update_form(request.form['id'], request.form['value'])
        self._post_update(request.form['id'])
        return redirect(url_for('settings_variable_list'))

    def _pre_update(self, id: int) -> Optional[str]:
        variable = self._model_store.variable().get(id)

        if variable.name == 'playlist_enabled':
            fleet_player_enabled = self._model_store.variable().get_one_by_name(name='fleet_player_enabled')
            if variable.as_bool() and fleet_player_enabled.as_bool():
                return self.t('settings_variable_form_error_not_playlist_enabled_while_fleet_player_enabled')

        return None

    def _post_update(self, id: int) -> None:
        variable = self._model_store.variable().get(id)

        if variable.refresh_player:
            self._model_store.variable().update_by_name("refresh_player_request", time.time())

        if variable.name == 'slide_upload_limit':
            self.reload_web_server()

        if variable.name == 'fleet_studio_enabled':
            self.reload_web_server()

        if variable.name == 'fleet_player_enabled':
            playlist_enabled = self._model_store.variable().get_one_by_name(name='playlist_enabled')
            if variable.as_bool() and not playlist_enabled.as_bool():
                self._model_store.variable().update_by_name(name='playlist_enabled', value=True)

            self.reload_web_server()

        if variable.name == 'auth_enabled':
            if variable.as_bool() and self._model_store.user().count_all_enabled() == 0:
                self._model_store.user().add_form(User(username="admin", password="admin", enabled=True))

            self.reload_web_server()

        if variable.name == 'lang':
            self._model_store.lang().set_lang(variable.value)
            self._model_store.variable().reload()

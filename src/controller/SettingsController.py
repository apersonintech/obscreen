import time
import json
import threading

from flask import Flask, render_template, redirect, request, url_for
from typing import Optional

from src.service.ModelStore import ModelStore
from src.interface.ObController import ObController
from src.model.entity.User import User
from src.util.utils import restart


class SettingsController(ObController):

    def register(self):
        self._app.add_url_rule('/settings/variable/list', 'settings_variable_list', self._auth(self.settings_variable_list), methods=['GET'])
        self._app.add_url_rule('/settings/variable/edit', 'settings_variable_edit', self._auth(self.settings_variable_edit), methods=['POST'])
        self._app.add_url_rule('/settings/variable-plugin/list', 'settings_variable_plugin_list', self._auth(self.settings_variable_plugin_list), methods=['GET'])
        self._app.add_url_rule('/settings/variable-plugin/edit', 'settings_variable_plugin_edit', self._auth(self.settings_variable_plugin_edit), methods=['POST'])

    def settings_variable_list(self):
        self._model_store.variable().update_by_name('last_pillmenu_configuration', 'settings_variable_list')

        return render_template(
            'configuration/settings/list.jinja.html',
            variables=self._model_store.variable().get_editable_variables(plugin=False, sort='section'),
        )

    def settings_variable_plugin_list(self):
        self._model_store.variable().update_by_name('last_pillmenu_configuration', 'settings_variable_plugin_list')

        return render_template(
            'configuration/plugins/list.jinja.html',
            plugins=self._model_store.plugins(),
            variables=self._model_store.variable().get_editable_variables(plugin=True, sort='plugin'),
        )

    def settings_variable_edit(self):
        error = self._pre_update(request.form['id'])

        if error:
            return redirect(url_for('settings_variable_list', error=error))

        self._model_store.variable().update_form(request.form['id'], request.form['value'])
        redirect_response = self._post_update(request.form['id'])

        if redirect_response:
            return redirect_response

        return redirect(url_for('settings_variable_list'))

    def settings_variable_plugin_edit(self):
        error = self._pre_update(request.form['id'])

        if error:
            return redirect(url_for('settings_variable_plugin_list', error=error))

        self._model_store.variable().update_form(request.form['id'], request.form['value'])
        redirect_response = self._post_update(request.form['id'])

        if redirect_response:
            return redirect_response

        return redirect(url_for('settings_variable_plugin_list'))

    def _pre_update(self, id: int) -> Optional[str]:
        variable = self._model_store.variable().get(id)

        return None

    def _post_update(self, id: int) -> None:
        variable = self._model_store.variable().get(id)

        if variable.refresh_player:
            self._model_store.variable().update_by_name("refresh_player_request", time.time())

        self._model_store.variable().reload()

        if variable.name == 'slide_upload_limit':
            self.reload_web_server()
            return redirect(url_for('settings_variable_list', warning='common_restart_needed'))

        if variable.name == 'fleet_player_enabled':
            self.reload_web_server()

        if variable.name == 'auth_enabled':
            if variable.as_bool() and self._model_store.user().count_all_enabled() == 0:
                self._model_store.user().add_form(User(username="admin", password="admin", enabled=True))

            self.reload_web_server()
            return redirect(url_for('logout'))

        if variable.name == 'lang':
            self.reload_lang(variable.value)

        if variable.is_from_plugin():
            thread = threading.Thread(target=self.plugin_update)
            thread.daemon = True
            thread.start()
            return redirect(url_for('settings_variable_plugin_list', warning='common_restart_needed'))

    def plugin_update(self) -> None:
        restart()

import os
import sys
import platform
import subprocess
import threading
import time

from flask import Flask, render_template, jsonify, request, url_for, redirect
from src.manager.VariableManager import VariableManager
from src.manager.ConfigManager import ConfigManager
from src.service.ModelStore import ModelStore

from src.interface.ObController import ObController
from src.util.utils import restart
from src.util.UtilNetwork import get_ip_address
from src.service.Sysinfo import get_all_sysinfo


class SysinfoController(ObController):

    def register(self):
        self._app.add_url_rule('/sysinfo', 'sysinfo_attribute_list', self._auth(self.sysinfo), methods=['GET'])
        self._app.add_url_rule('/sysinfo/restart', 'sysinfo_restart', self.sysinfo_restart, methods=['GET', 'POST'])
        self._app.add_url_rule('/sysinfo/restart/needed', 'sysinfo_restart_needed', self._auth(self.sysinfo_restart_needed), methods=['GET'])
        self._app.add_url_rule('/sysinfo/get/ipaddr', 'sysinfo_get_ipaddr', self._auth(self.sysinfo_get_ipaddr), methods=['GET'])

    def sysinfo(self):
        return render_template(
            'sysinfo/list.jinja.html',
            sysinfo=get_all_sysinfo(),
            last_logs=self._model_store.logging().get_last_lines_of_stdout(100),
            ro_variables=self._model_store.variable().get_readonly_variables(),
            env_variables=self._model_store.config().map()
        )

    def sysinfo_restart(self):
        debug = self._model_store.config().map().get('debug')
        secret = self._model_store.config().map().get('secret_key')
        challenge = request.args.get('secret_key')

        if secret != challenge:
            return jsonify({'status': 'error'})

        thread = threading.Thread(target=restart, args=(debug,))
        thread.daemon = True
        thread.start()

        return redirect(url_for('manage'))

    def sysinfo_restart_needed(self):
        var_last_slide_update = self._model_store.variable().get_one_by_name('last_slide_update')
        var_last_restart = self._model_store.variable().get_one_by_name('last_restart')

        if var_last_slide_update.value <= var_last_restart.value:
            return jsonify({'status': False})

        return jsonify({'status': True})

    def sysinfo_get_ipaddr(self):
        ipaddr = get_ip_address()
        return ipaddr if ipaddr else ''

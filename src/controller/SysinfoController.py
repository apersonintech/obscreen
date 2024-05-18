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
from src.utils import get_ip_address, am_i_in_docker


class SysinfoController(ObController):

    def register(self):
        self._app.add_url_rule('/sysinfo', 'sysinfo_attribute_list', self._auth(self.sysinfo), methods=['GET'])
        self._app.add_url_rule('/sysinfo/restart', 'sysinfo_restart', self.sysinfo_restart, methods=['GET', 'POST'])
        self._app.add_url_rule('/sysinfo/restart/needed', 'sysinfo_restart_needed', self._auth(self.sysinfo_restart_needed), methods=['GET'])

    def sysinfo(self):
        ipaddr = get_ip_address()
        return render_template(
            'sysinfo/list.jinja.html',
            ipaddr=ipaddr if ipaddr else self._model_store.lang().map().get('common_unknown_ipaddr'),
            ro_variables=self._model_store.variable().get_readonly_variables(),
            env_variables=self._model_store.config().map()
        )

    def sysinfo_restart(self):
        secret = self._model_store.config().map().get('secret_key')
        challenge = request.args.get('secret_key')
        thread = threading.Thread(target=self.restart, args=(secret, challenge))
        thread.daemon = True
        thread.start()

        return redirect(url_for('manage'))

    def sysinfo_restart_needed(self):
        var_last_slide_update = self._model_store.variable().get_one_by_name('last_slide_update')
        var_last_restart = self._model_store.variable().get_one_by_name('last_restart')

        if var_last_slide_update.value <= var_last_restart.value:
            return jsonify({'status': False})

        return jsonify({'status': True})

    def restart(self, secret: str, challenge: str) -> None:
        time.sleep(1)

        if secret != challenge:
            return jsonify({'status': 'error'})

        if platform.system().lower() == 'darwin':
            if self._model_store.config().map().get('debug'):
                python = sys.executable
                os.execl(python, python, *sys.argv)
        elif am_i_in_docker():
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            try:
                subprocess.run(["sudo", "systemctl", "restart", 'obscreen-manager'], check=True, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pass
            except subprocess.TimeoutExpired:
                pass
            except subprocess.CalledProcessError:
                pass

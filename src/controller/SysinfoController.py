import os
import sys
import platform
import subprocess

from flask import Flask, render_template, jsonify
from src.manager.VariableManager import VariableManager
from src.manager.ConfigManager import ConfigManager
from src.utils import get_ip_address


class SysinfoController:

    def __init__(self, app, lang_dict, config_manager: ConfigManager, variable_manager: VariableManager):
        self._app = app
        self._lang_dict = lang_dict
        self._config_manager = config_manager
        self._variable_manager = variable_manager
        self.register()

    def register(self):
        self._app.add_url_rule('/sysinfo', 'sysinfo_attribute_list', self.sysinfo, methods=['GET'])
        self._app.add_url_rule('/sysinfo/restart', 'sysinfo_restart', self.sysinfo_restart, methods=['POST'])
        self._app.add_url_rule('/sysinfo/restart/needed', 'sysinfo_restart_needed', self.sysinfo_restart_needed, methods=['GET'])

    def sysinfo(self):
        ipaddr = get_ip_address()
        return render_template(
            'sysinfo/list.jinja.html',
            ipaddr=ipaddr if ipaddr else self._lang_dict['common_unknown_ipaddr'],
            l=self._lang_dict,
            ro_variables=self._variable_manager.get_readonly_variables(),
        )

    def sysinfo_restart(self):
        if platform.system().lower() == 'darwin':
            if self._config_manager.map().get('debug'):
                python = sys.executable
                os.execl(python, python, *sys.argv)
        else:
            try:
                subprocess.run(["sudo", "systemctl", "restart", 'obscreen'], check=True, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pass
            except subprocess.TimeoutExpired:
                pass
            except subprocess.CalledProcessError:
                pass

        return jsonify({'status': 'ok'})

    def sysinfo_restart_needed(self):
        var_last_slide_update = self._variable_manager.get_one_by_name('last_slide_update')
        var_last_restart = self._variable_manager.get_one_by_name('last_restart')

        if var_last_slide_update.value <= var_last_restart.value:
            return jsonify({'status': False})

        return jsonify({'status': True})


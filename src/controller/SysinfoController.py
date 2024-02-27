import os
import sys
import platform
import subprocess

from flask import Flask, render_template, jsonify
from src.utils import get_ip_address


class SysinfoController:

    def __init__(self, app, lang_dict, config):
        self._app = app
        self._lang_dict = lang_dict
        self._config = config
        self.register()

    def register(self):
        self._app.add_url_rule('/sysinfo', 'sysinfo_attribute_list', self.sysinfo, methods=['GET'])
        self._app.add_url_rule('/sysinfo/restart', 'sysinfo_restart', self.sysinfo_restart, methods=['POST'])

    def sysinfo(self):
        return render_template(
            'sysinfo/list.jinja.html',
            ipaddr=get_ip_address(),
            l=self._lang_dict,
        )

    def sysinfo_restart(self):
        if platform.system().lower() == 'darwin':
            if self._config['debug']:
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


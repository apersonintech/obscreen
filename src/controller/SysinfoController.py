import json

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from src.utils import get_ip_address


class SysinfoController:

    def __init__(self, app, l):
        self._app = app
        self._l = l
        self.register()

    def register(self):
        self._app.add_url_rule('/sysinfo', 'sysinfo_attribute_list', self.sysinfo, methods=['GET'])

    def sysinfo(self):
        return render_template(
            'sysinfo/list.jinja.html',
            ipaddr=get_ip_address(),
            l=self._l,
        )

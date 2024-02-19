#!/usr/bin/python3
import json
import os
import re
import shutil
import subprocess
import sys

from enum import Enum
from flask import Flask, render_template, redirect, request, url_for, send_from_directory
from pysondb import db
from config import config


# <classes>
class ItemType(Enum):
    PICTURE = 'picture'
    VIDEO = 'video'
    URL = 'url'
# </classes>

# <config>
PLAYER_URL = 'http://localhost:{}'.format(config['port'])
DB = db.getDb("data/slideshow.json")
with open('./lang/{}.json'.format(config['lang']), 'r') as file:
    LANGDICT = json.load(file)
# </config>

# <reverse-proxy>
if config['reverse_proxy_mode']:
    reverse_proxy_config_file = 'system/nginx-reclame'
    with open(reverse_proxy_config_file, 'r') as file:
        content = file.read()
    with open(reverse_proxy_config_file, 'w') as file:
        file.write(re.sub(r'proxy_pass .*?;', 'proxy_pass {};'.format(PLAYER_URL), content))
    PLAYER_URL = 'http://localhost'
# </reverse-proxy>

# <server>
app = Flask(__name__, template_folder='views', static_folder='data')

if config['debug']:
    app.config['TEMPLATES_AUTO_RELOAD'] = True
# </server>

# <xenv>
destination_path = '/home/pi/.config/lxsession/LXDE-pi/autostart'
os.makedirs(os.path.dirname(destination_path), exist_ok=True)
xenv_presets = f"""
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
#@point-rpi
@xset s off
@xset -dpms
@xset s noblank
@unclutter -display :0 -noevents -grab
@sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' ~/.config/chromium/Default/Preferences
#@sleep 10
@chromium-browser --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --disable-restore-session-state --noerrdialogs --kiosk --incognito --window-position=0,0 --display=:0 {PLAYER_URL}
"""
with open(destination_path, 'w') as file:
    file.write(xenv_presets)
# </xenv>

# <utils>
def get_ip_address():
    try:
        result = subprocess.run(
            ["ip", "-4", "route", "get", "8.8.8.8"],
            capture_output=True,
            text=True
        )
        ip_address = result.stdout.split()[6]
        return ip_address
    except Exception as e:
        print(f"Error obtaining IP address: {e}")
        return 'Unknown'
# </utils>

# <web>
@app.route('/')
def index():
    return render_template('player.jinja.html', items=json.dumps(DB.getAll()))

@app.route('/slide/default')
def slide_default():
    return render_template('default.jinja.html', ipaddr=get_ip_address())

@app.route('/manage')
def manage():
    return render_template('manage.jinja.html', ipaddr=get_ip_address(), l=LANGDICT)

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('data', '404.html'), 404
# </web>

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['port'])


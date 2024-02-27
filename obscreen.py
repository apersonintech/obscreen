#!/usr/bin/python3
import json
import os
import re
import shutil
import subprocess
import sys


from flask import Flask, send_from_directory
from src.manager.SlideManager import SlideManager
from src.manager.ScreenManager import ScreenManager
from src.manager.VariableManager import VariableManager
from src.controller.PlayerController import PlayerController
from src.controller.SlideshowController import SlideshowController
from src.controller.FleetController import FleetController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController
from config import config

# <config>
variable_manager = VariableManager()
vars = variable_manager.get_variable_map()

screen_manager = ScreenManager()
slide_manager = SlideManager()

PLAYER_URL = 'http://localhost:{}'.format(vars['port'].as_int())
with open('./lang/{}.json'.format(vars['lang'].as_string()), 'r') as file:
    LANGDICT = json.load(file)

variable_manager.init(LANGDICT)
# </config>


# <reverse-proxy>
if config['reverse_proxy_mode']:
    reverse_proxy_config_file = 'system/nginx-obscreen'
    with open(reverse_proxy_config_file, 'r') as file:
        content = file.read()
    with open(reverse_proxy_config_file, 'w') as file:
        file.write(re.sub(r'proxy_pass .*?;', 'proxy_pass {};'.format(PLAYER_URL), content))
    PLAYER_URL = 'http://localhost'
# </reverse-proxy>


# <server>
app = Flask(__name__, template_folder='views', static_folder='data')
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

if config['debug']:
    app.config['TEMPLATES_AUTO_RELOAD'] = True

# </server>


# <xenv>
if config['lx_file']:
    destination_path = '/home/pi/.config/lxsession/LXDE-pi/autostart'
    os.makedirs(os.path.dirname(config['lx_file']), exist_ok=True)
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
    with open(config['lx_file'], 'w') as file:
        file.write(xenv_presets)
# </xenv>


# <web>
@app.context_processor
def inject_global_vars():
    return dict(
        FLEET_ENABLED=vars['fleet_enabled'].as_bool(),
        LANG=vars['lang'].as_string(),
        STATIC_PREFIX='/data/www/'
    )


PlayerController(app, LANGDICT, slide_manager)
SlideshowController(app, LANGDICT, slide_manager)
SettingsController(app, LANGDICT, variable_manager)
SysinfoController(app, LANGDICT, config)

if vars['fleet_enabled'].as_bool():
    FleetController(app, LANGDICT, screen_manager)

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('views', 'core/error404.html'), 404
# </web>


if __name__ == '__main__':
    app.run(
        host=vars['bind'].as_string(),
        port=vars['port'].as_int(),
        debug=config['debug']
    )


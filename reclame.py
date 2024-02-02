#!/usr/bin/python3

from flask import Flask, render_template, redirect, request, url_for, send_from_directory
import json
import os
import re
import shutil
import subprocess

# <server>
app = Flask(__name__, template_folder='views', static_folder='data')
port = 5000
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
@chromium-browser --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --disable-restore-session-state --noerrdialogs --kiosk --incognito --window-position=0,0 --display=:0 http://localhost:{port}
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
    with open('./data/slideshow.json', 'r') as file:
        items = json.load(file)

    return render_template('player.jinja.html', port=port, items=json.dumps(items))

@app.route('/slide/default')
def slide_default():
    return render_template('default.jinja.html', ipaddr=get_ip_address())

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('data', '404.html'), 404
# </web>

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

#!/usr/bin/python3
import json
import os
import re
import shutil
import subprocess
import sys


from enum import Enum
from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from config import config
from src.SlideManager import SlideManager
from src.model.Slide import Slide
from src.model.SlideType import SlideType
from src.utils import str_to_enum



# <config>
PLAYER_URL = 'http://localhost:{}'.format(config['port'])
slide_manager = SlideManager()
with open('./lang/{}.json'.format(config['lang']), 'r') as file:
    LANGDICT = json.load(file)
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
if config['lxfile']:
    destination_path = '/home/pi/.config/lxsession/LXDE-pi/autostart'
    os.makedirs(os.path.dirname(config['lxfile']), exist_ok=True)
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
    with open(config['lxfile'], 'w') as file:
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
    return render_template('player.jinja.html', items=json.dumps(slide_manager.to_dict(slide_manager.get_enabled_slides())))

@app.route('/playlist')
def playlist():
    return jsonify(slide_manager.to_dict(slide_manager.get_enabled_slides()))

@app.route('/slide/default')
def slide_default():
    return render_template('default.jinja.html', ipaddr=get_ip_address())

@app.route('/manage')
def manage():
    return render_template(
        'manage.jinja.html',
        ipaddr=get_ip_address(),
        l=LANGDICT,
        enabled_slides=slide_manager.get_enabled_slides(),
        disabled_slides=slide_manager.get_disabled_slides()
    )

@app.route('/manage/slide/add', methods=['GET', 'POST'])
def manage_slide_add():
    slide = Slide(
        name=request.form['name'],
        type=str_to_enum(request.form['type'], SlideType),
        duration=request.form['duration'],
    )

    if slide.has_file():
        if 'object' not in request.files:
            return redirect(request.url)

        object = request.files['object']

        if object.filename == '':
            return redirect(request.url)

        if object:
            object_name = secure_filename(object.filename)
            object_path = os.path.join(app.config['UPLOAD_FOLDER'], object_name)
            object.save(object_path)
            slide.location = object_path
    else:
        slide.location = request.form['object']

    slide_manager.add_form(slide)

    return redirect(url_for('manage'))

@app.route('/manage/slide/edit', methods=['POST'])
def manage_slide_edit():
    slide_manager.update_form(request.form['id'], request.form['name'], request.form['duration'])
    return redirect(url_for('manage'))

@app.route('/manage/slide/toggle', methods=['POST'])
def manage_slide_toggle():
    data = request.get_json()
    slide_manager.update_enabled(data.get('id'), data.get('enabled'))
    return jsonify({'status': 'ok'})

@app.route('/manage/slide/delete', methods=['DELETE'])
def manage_slide_delete():
    data = request.get_json()
    slide_manager.delete(data.get('id'))
    return jsonify({'status': 'ok'})

@app.route('/manage/slide/position', methods=['POST'])
def manage_slide_position():
    data = request.get_json()
    slide_manager.update_positions(data)
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('views', 'error404.html'), 404
# </web>

if __name__ == '__main__':
    app.run(
        host=config['bind'] if 'bind' in config else '0.0.0.0',
        port=config['port'],
        debug=config['debug']
    )


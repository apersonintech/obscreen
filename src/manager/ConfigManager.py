import re
import os
import sys
import logging
import argparse

from src.manager.VariableManager import VariableManager
from src.utils import am_i_in_docker
from dotenv import load_dotenv
load_dotenv()

class ConfigManager:

    DEFAULT_PORT = 5000
    DEFAULT_PLAYER_AUTOSTART_PATH = './var/run/play'
    VERSION_FILE = 'version.txt'

    def __init__(self, variable_manager: VariableManager):
        self._variable_manager = variable_manager
        self._CONFIG = {
            'version': None,
            'port': self.DEFAULT_PORT,
            'bind': '0.0.0.0',
            'debug': False,
            'player_autostart_file': self.DEFAULT_PLAYER_AUTOSTART_PATH,
            'log_file': None,
            'log_level': 'INFO',
            'log_stdout': True,
            'secret_key': 'ANY_SECRET_KEY_HERE',
            'player_url': 'http://localhost:{}'.format(self.DEFAULT_PORT)
        }

        self.load_version()
        self.load_from_env()
        self.load_from_args()

        self._CONFIG['port'] = self._CONFIG['port'] if self._CONFIG['port'] else self.DEFAULT_PORT

        self.autoconfigure()

        if self.map().get('debug'):
            logging.debug(self._CONFIG)

    def map(self) -> dict:
        return self._CONFIG

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Obscreen")
        parser.add_argument('--debug', '-d', default=self._CONFIG['debug'], help='Debug mode')
        parser.add_argument('--port', '-p', default=self._CONFIG['port'], help='Application port')
        parser.add_argument('--bind', '-b', default=self._CONFIG['bind'], help='Application bind address')
        parser.add_argument('--secret-key', '-s', default=self._CONFIG['secret_key'], help='Application secret key (any random string)')
        parser.add_argument('--player-autostart-file', '-x', default=self._CONFIG['player_autostart_file'], help='Path to player autostart file')
        parser.add_argument('--log-file', '-lf', default=self._CONFIG['log_file'], help='Log File path')
        parser.add_argument('--log-level', '-ll', default=self._CONFIG['log_level'], help='Log Level')
        parser.add_argument('--log-stdout', '-ls', default=self._CONFIG['log_stdout'], action='store_true', help='Log to standard output')
        parser.add_argument('--version', '-v', default=None, action='store_true', help='Get version number')

        return parser.parse_args()

    def load_version(self) -> str:
        with open(self.VERSION_FILE, 'r') as file:
            self._CONFIG['version'] = file.read()

    def load_from_args(self) -> None:
        args = self.parse_arguments()

        if args.debug:
            self._CONFIG['debug'] = args.debug
        if args.player_autostart_file:
            self._CONFIG['player_autostart_file'] = args.player_autostart_file
        if args.log_file:
            self._CONFIG['log_file'] = args.log_file
        if args.secret_key:
            self._CONFIG['secret_key'] = args.secret_key
        if args.log_level:
            self._CONFIG['log_level'] = args.log_level
        if args.log_stdout:
            self._CONFIG['log_stdout'] = args.log_stdout
        if args.version:
            print("Obscreen version v{} (https://github.com/jr-k/obscreen)".format(self._CONFIG['version']))
            sys.exit(0)

    def load_from_env(self) -> None:
        for key in self._CONFIG:
            if key.upper() in os.environ:
                value = os.environ[key.upper()]
                if value.lower() == 'false' or value == '0' or value == '':
                    value = False
                elif value.lower() == 'true' or value == '1':
                    value = True
                self._CONFIG[key.lower()] = value
                logging.info(f"Env var {key} has been found")

    def autoconfigure(self) -> None:
        self.autoconfigure_player_url()

        if self.map().get('player_autostart_file'):
            self.autoconfigure_player_autostart_file()


    def autoconfigure_player_url(self) -> str:
        self._CONFIG['player_url'] = 'http://localhost:{}'.format(self.map().get('port'))

        return self._CONFIG['player_url']

    def autoconfigure_player_autostart_file(self) -> None:
        path = self.map().get('player_autostart_file')
        in_docker = am_i_in_docker()
        player_autostart_path = self.DEFAULT_PLAYER_AUTOSTART_PATH if in_docker else path

        if os.path.isdir(path) or not os.path.exists(path):
            if not in_docker:
                open(player_autostart_path, 'a').close()
            else:
                logging.error(
                    "Player autostart file {} doesn't exist on your server'\n".format(
                        player_autostart_path
                    )
                )
                sys.exit(1)
        else:
            logging.info("Overriding player autostart file {}".format(player_autostart_path))

        player_url = self.map().get('player_url')
        os.makedirs(os.path.dirname(player_autostart_path), exist_ok=True)
        xenv_presets = """#!/bin/bash

# Disable screensaver and DPMS
xset s off
xset -dpms
xset s noblank

# Start unclutter to hide the mouse cursor
unclutter -display :0 -noevents -grab &

# Modify Chromium preferences to avoid restore messages
mkdir -p __HOME__/.config/chromium/Default 2>/dev/null
touch __HOME__/.config/chromium/Default/Preferences
sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' __HOME__/.config/chromium/Default/Preferences

RESOLUTION=$(DISPLAY=:0 xrandr | grep '*' | awk '{print $1}')
WIDTH=$(echo $RESOLUTION | cut -d 'x' -f 1)
HEIGHT=$(echo $RESOLUTION | cut -d 'x' -f 2)

# Start Chromium in kiosk mode
chromium-browser --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --noerrdialogs --kiosk --incognito --window-position=0,0 --window-size=${WIDTH},${HEIGHT} --display=:0 __PLAYER_URL__
        """.replace('__PLAYER_URL__', player_url).replace('__HOME__', os.environ['HOME'])
        with open(player_autostart_path, 'w') as file:
            file.write(xenv_presets)

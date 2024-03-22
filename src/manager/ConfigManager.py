import re
import os
import json
import logging
import argparse

from src.manager.VariableManager import VariableManager


class ConfigManager:

    CONFIG_FILE = 'config.json'

    def __init__(self, variable_manager: VariableManager):
        self._variable_manager = variable_manager
        self._CONFIG = {
            'debug': False,
            'reverse_proxy_mode': False,
            'lx_file': '/home/pi/.config/lxsession/LXDE-pi/autostart',
            'log_file': None,
            'log_level': 'INFO',
            'log_stdout': True,
            'player_url': 'http://localhost:{}'.format(self._variable_manager.map().get('port').as_int())
        }

        self.load_from_json(file_path=self.CONFIG_FILE)
        self.load_from_env()
        self.load_from_args()
        self.autoconfigure()

        if self.map().get('debug'):
            logging.debug(self._CONFIG)

    def map(self) -> dict:
        return self._CONFIG

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Obscreen")
        parser.add_argument('--debug', '-d', default=self._CONFIG['debug'], help='Debug mode')
        parser.add_argument('--reverse_proxy_mode', '-r', default=self._CONFIG['reverse_proxy_mode'], action='store_true',  help='true if you want to use nginx on port 80')
        parser.add_argument('--lx-file', '-x', default=self._CONFIG['lx_file'], help='Path to lx autostart file')
        parser.add_argument('--log-file', '-lf', default=self._CONFIG['log_file'], help='Log File path')
        parser.add_argument('--log-level', '-ll', default=self._CONFIG['log_level'], help='Log Level')
        parser.add_argument('--log-stdout', '-ls', default=self._CONFIG['log_stdout'], action='store_true', help='Log to standard output')

        return parser.parse_args()

    def load_from_args(self) -> None:
        args = self.parse_arguments()

        if args.debug:
            self._CONFIG['debug'] = args.debug
        if args.reverse_proxy_mode:
            self._CONFIG['reverse_proxy_mode'] = args.reverse_proxy_mode
        if args.lx_file:
            self._CONFIG['lx_file'] = args.lx_file
        if args.log_file:
            self._CONFIG['log_file'] = args.log_file
        if args.log_level:
            self._CONFIG['log_level'] = args.log_level
        if args.log_stdout:
            self._CONFIG['log_stdout'] = args.log_stdout

    def load_from_json(self, file_path: str) -> None:
        try:
            with open(file_path, 'r') as file:
                json_config = json.load(file)
                for key in json_config:
                    self._CONFIG[key] = json_config[key]
                    logging.info(f"Json var {key} has been found")
        except FileNotFoundError:
            logging.error(f"Json configuration file {file_path} doesn't exist.")

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
        if self.map().get('reverse_proxy_mode'):
            self.autoconfigure_nginx()

        if self.map().get('lx_file'):
            self.autoconfigure_lxconf()

    def autoconfigure_nginx(self) -> None:
        reverse_proxy_config_file = 'system/nginx-obscreen'
        with open(reverse_proxy_config_file, 'r') as file:
            content = file.read()
        with open(reverse_proxy_config_file, 'w') as file:
            file.write(re.sub(r'proxy_pass .*?;', 'proxy_pass {};'.format(self.map().get('player_url')), content))

        self._CONFIG['player_url'] = 'http://localhost'

    def autoconfigure_lxconf(self) -> None:
        destination_path = self.map().get('lx_file')
        player_url = self.map().get('player_url')
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
@chromium-browser --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --disable-restore-session-state --noerrdialogs --kiosk --incognito --window-position=0,0 --display=:0 {player_url}
        """
        with open(destination_path, 'w') as file:
            file.write(xenv_presets)


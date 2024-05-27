import logging
import platform

from flask import Flask, redirect, url_for

from src.interface.ObController import ObController
from src.utils import run_system_command, sudo_run_system_command, get_working_directory, am_i_in_docker
from src.Application import Application


class GitUpdaterController(ObController):

    def register(self):
        self._app.add_url_rule('/git-updater/update/now', 'git_updater_update_now', self._auth(self.update_now), methods=['GET'])

    def update_now(self):
        if am_i_in_docker:
            logging.warn('You are using Docker, you can\'t use Git Updater plugin')
        else:
            os_name = platform.system().lower()

            if os_name == "linux":
                logging.warn('Git Updater supports linux dependency manager, using apt...')
                sudo_run_system_command(['apt', 'install'] + 'git python3-pip python3-venv libsqlite3-dev'.split(' '))
            elif os_name == "windows":
                logging.warn('Git Updater doesn\'t support windows dependency manager, install system dependencies manually')
            elif os_name == "darwin":
                logging.warn('Git Updater doesn\'t support macos dependency manager, install system dependencies manually with homebrew')

            run_system_command(['git', '-C', get_working_directory(), 'stash'])
            run_system_command(['git', '-C', get_working_directory(), 'checkout', 'tags/v{}'.format(Application.get_version())])
            run_system_command(['git', '-C', get_working_directory(), 'pull'])
            run_system_command(['pip3', 'install', '-r', 'requirements.txt'])
            sudo_run_system_command(['systemctl', 'restart', Application.get_name()])

        return redirect(url_for('sysinfo_attribute_list'))

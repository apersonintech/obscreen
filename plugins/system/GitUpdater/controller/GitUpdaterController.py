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
        old_version = Application.get_version()
        logging.info("🚧 Application update from {} to master...".format(old_version))

        if am_i_in_docker():
            logging.warn('You are using Docker, you can\'t use Git Updater plugin')
            return redirect(url_for('sysinfo_attribute_list'))

        os_name = platform.system().lower()

        if os_name == "linux":
            logging.warn('Git Updater supports linux dependency manager, using apt...')
            sudo_run_system_command(['apt', 'install'] + 'git python3-pip python3-venv libsqlite3-dev'.split(' '))
        elif os_name == "windows":
            logging.warn('Git Updater doesn\'t supports windows dependency manager, install system dependencies manually')
        elif os_name == "darwin":
            logging.warn('Git Updater doesn\'t supports macos dependency manager, install system dependencies manually with homebrew')

        run_system_command(['git', '-C', get_working_directory(), 'stash'])
        run_system_command(['git', '-C', get_working_directory(), 'checkout', 'master'])
        run_system_command(['git', '-C', get_working_directory(), 'pull'])
        run_system_command(['pip3', 'install', '-r', 'requirements.txt'])

        if os_name == "linux":
            logging.warn('Git Updater supports linux process manager, using apt...')
            sudo_run_system_command(['systemctl', 'restart', Application.get_name()])
        elif os_name == "windows":
            logging.warn('Git Updater doesn\'t fully supports windows process manager, you may need to restart application manually')
        elif os_name == "darwin":
            logging.warn('Git Updater doesn\'t fully supports macos process manager, you may need to restart application manually')

        new_version = Application.get_version()

        if old_version != new_version:
            logging.info("Application update succeeded to version {}".format(new_version))
        else:
            logging.info("Application already up to date with version {}".format(new_version))

        return redirect(url_for(
            'sysinfo_restart',
            secret_key=self._model_store.config().map().get('secret_key')
        ))

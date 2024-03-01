import sys
import logging

from src.manager.ConfigManager import ConfigManager


class LoggingManager:

    def __init__(self, config_manager: ConfigManager):
        c_map = config_manager.map()
        log_level_str = c_map.get('log_level', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        self._logger = logging.getLogger()
        self._logger.setLevel(log_level)

        if c_map.get('log_file'):
            self._add_file_handler(file_path=c_map.get('log_file'))

        if c_map.get('log_stdout'):
            self._add_stdout_handler()

    def _add_file_handler(self, file_path: str) -> None:
        file_handler = logging.FileHandler(file_path)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

    def _add_stdout_handler(self) -> None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)


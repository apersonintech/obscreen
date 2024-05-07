from enum import Enum
from typing import Union, Dict

from src.manager.LangManager import LangManager
from src.manager.DatabaseManager import DatabaseManager


class ModelManager:

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager):
        self._lang_manager = lang_manager
        self._database_manager = database_manager

    def t(self, token) -> Union[Dict, str]:
        return self.lang_manager.translate(token)

    @property
    def lang_manager(self) -> LangManager:
        return self._lang_manager

    @property
    def database_manager(self) -> DatabaseManager:
        return self._database_manager

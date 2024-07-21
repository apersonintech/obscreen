from typing import Dict

from src.manager.PlaylistManager import PlaylistManager
from src.manager.SlideManager import SlideManager
from src.manager.ContentManager import ContentManager
from src.manager.FolderManager import FolderManager
from src.manager.NodePlayerManager import NodePlayerManager
from src.manager.NodePlayerGroupManager import NodePlayerGroupManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.manager.LangManager import LangManager
from src.manager.DatabaseManager import DatabaseManager
from src.manager.ConfigManager import ConfigManager
from src.manager.LoggingManager import LoggingManager


class ModelStore:

    def __init__(self, kernel, get_plugins: Dict):
        self._get_plugins = get_plugins
        self._kernel = kernel

        # Core
        self._config_manager = ConfigManager(replacers={
            'application_dir': kernel.get_application_dir()
        })
        self._logging_manager = LoggingManager(config_manager=self._config_manager)

        # Pure
        self._lang_manager = LangManager()
        self._database_manager = DatabaseManager()

        # Dynamics
        self._user_manager = UserManager(lang_manager=self._lang_manager, database_manager=self._database_manager, on_user_delete=self.on_user_delete)
        self._variable_manager = VariableManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, config_manager=self._config_manager)
        self._lang_manager.set_lang(self.variable().map().get('lang').as_string())

        # Model
        self._folder_manager = FolderManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager)
        self._node_player_manager = NodePlayerManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager)
        self._node_player_group_manager = NodePlayerGroupManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager)
        self._playlist_manager = PlaylistManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager)
        self._slide_manager = SlideManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager)
        self._content_manager = ContentManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager, variable_manager=self._variable_manager, config_manager=self._config_manager)
        self._variable_manager.reload()

    def logging(self) -> LoggingManager:
        return self._logging_manager

    def config(self) -> ConfigManager:
        return self._config_manager

    def variable(self) -> VariableManager:
        return self._variable_manager

    def database(self) -> DatabaseManager:
        return self._database_manager

    def slide(self) -> SlideManager:
        return self._slide_manager

    def content(self) -> ContentManager:
        return self._content_manager

    def playlist(self) -> PlaylistManager:
        return self._playlist_manager

    def node_player(self) -> NodePlayerManager:
        return self._node_player_manager

    def node_player_group(self) -> NodePlayerGroupManager:
        return self._node_player_group_manager

    def folder(self) -> FolderManager:
        return self._folder_manager

    def lang(self) -> LangManager:
        return self._lang_manager

    def user(self) -> UserManager:
        return self._user_manager

    def plugins(self) -> Dict:
        return self._get_plugins()

    def on_user_delete(self, user_id: int) -> None:
        self._playlist_manager.forget_for_user(user_id)
        self._folder_manager.forget_for_user(user_id)
        self._node_player_group_manager.forget_for_user(user_id)
        self._node_player_manager.forget_for_user(user_id)
        self._slide_manager.forget_for_user(user_id)
        self._content_manager.forget_for_user(user_id)
        self._user_manager.forget_for_user(user_id)

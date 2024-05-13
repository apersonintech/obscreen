from src.manager.SlideManager import SlideManager
from src.manager.ScreenManager import ScreenManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.manager.LangManager import LangManager
from src.manager.DatabaseManager import DatabaseManager
from src.manager.ConfigManager import ConfigManager
from src.manager.LoggingManager import LoggingManager


class ModelStore:

    def __init__(self):
        # Pure
        self._lang_manager = LangManager()
        self._database_manager = DatabaseManager()

        # Dynamics
        self._user_manager = UserManager(lang_manager=self._lang_manager, database_manager=self._database_manager, on_user_delete=self.on_user_delete)
        self._variable_manager = VariableManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager)
        self._lang_manager.set_lang(self.variable().map().get('lang').as_string())

        # Core
        self._config_manager = ConfigManager(variable_manager=self._variable_manager)
        self._logging_manager = LoggingManager(config_manager=self._config_manager)

        # Model
        self._screen_manager = ScreenManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager)
        self._slide_manager = SlideManager(lang_manager=self._lang_manager, database_manager=self._database_manager, user_manager=self._user_manager)
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

    def screen(self) -> ScreenManager:
        return self._screen_manager

    def lang(self) -> LangManager:
        return self._lang_manager

    def user(self) -> UserManager:
        return self._user_manager

    def on_user_delete(self, user_id: str):
        self._slide_manager.forget_user(user_id)

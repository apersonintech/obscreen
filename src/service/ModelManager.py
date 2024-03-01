from src.manager.SlideManager import SlideManager
from src.manager.ScreenManager import ScreenManager
from src.manager.VariableManager import VariableManager
from src.manager.LangManager import LangManager
from src.manager.ConfigManager import ConfigManager
from src.manager.LoggingManager import LoggingManager


class ModelManager:

    def __init__(self):
        self._variable_manager = VariableManager()
        self._config_manager = ConfigManager(variable_manager=self._variable_manager)
        self._logging_manager = LoggingManager(config_manager=self._config_manager)
        self._screen_manager = ScreenManager()
        self._slide_manager = SlideManager()
        self._lang_manager = LangManager(lang=self.variable().map().get('lang').as_string())
        self._variable_manager.reload(lang_map=self._lang_manager.map())

    def logging(self) -> LoggingManager:
        return self._logging_manager

    def config(self) -> ConfigManager:
        return self._config_manager

    def variable(self) -> VariableManager:
        return self._variable_manager

    def slide(self) -> SlideManager:
        return self._slide_manager

    def screen(self) -> ScreenManager:
        return self._screen_manager

    def lang(self) -> LangManager:
        return self._lang_manager


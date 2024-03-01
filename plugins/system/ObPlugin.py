import abc

from typing import Optional, List, Dict, Union
from src.model.Variable import Variable
from src.model.VariableType import VariableType
from src.model.HookType import HookType
from src.model.HookRegistration import HookRegistration
from src.service.ModelStore import ModelStore


class ObPlugin(abc.ABC):

    PLUGIN_PREFIX = "plugin_"

    def __init__(self, directory: str, model_store: ModelStore):
        self._directory = directory
        self._model_store = model_store

    @abc.abstractmethod
    def use_id(self) -> str:
        pass

    @abc.abstractmethod
    def use_title(self) -> str:
        pass

    @abc.abstractmethod
    def use_variables(self) -> List[Variable]:
        pass

    @abc.abstractmethod
    def use_hooks_registrations(self) -> List[HookRegistration]:
        pass

    def get_directory(self) -> Optional[str]:
        return self._directory

    def get_plugin_variable_prefix(self) -> str:
        return "{}{}".format(self.PLUGIN_PREFIX, self.use_id())

    def get_plugin_variable_name(self, name: str) -> str:
        return "{}_{}".format(self.get_plugin_variable_prefix(), name)

    def set_variable(self, name: str, value, type: VariableType, editable: bool, description: str) -> Variable:
        return self._model_store.variable().set_variable(
            name=self.get_plugin_variable_name(name), value=value, type=type, editable=editable, description=description
        )

    def set_hook_registration(self, hook: HookType, priority: int = 0) -> HookRegistration:
        return HookRegistration(plugin=self, hook=hook, priority=priority)

from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from typing import Optional


class FunctionalHookRegistration(HookRegistration):

    def __init__(self, plugin, hook: HookType, priority: int = 0, function=None):
        super().__init__(plugin, hook, priority)
        self._function = function

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        self._function = value

    def __str__(self) -> str:
        return f"FunctionalHookRegistration(" \
               f"plugin='{self.plugin.get_id()}',\n" \
               f"hook='{self.hook}',\n" \
               f"priority='{self.priority}',\n" \
               f"function='{self.function}',\n" \
               f")"
    
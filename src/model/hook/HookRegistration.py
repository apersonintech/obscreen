from src.model.enum.HookType import HookType


class HookRegistration:

    def __init__(self, plugin, hook: HookType, priority: int = 0):
        self._plugin = plugin
        self._hook = hook
        self._priority = priority

    @property
    def plugin(self):
        return self._plugin

    @plugin.setter
    def plugin(self, value):
        self._plugin = value

    @property
    def hook(self) -> HookType:
        return self._hook

    @hook.setter
    def hook(self, value: HookType):
        self._hook = value

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self._priority = value

    def __str__(self) -> str:
        return f"HookRegistration(" \
               f"plugin='{self.plugin.get_id()}',\n" \
               f"hook='{self.hook}',\n" \
               f"priority='{self.priority}',\n" \
               f")"
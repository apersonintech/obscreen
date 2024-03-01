from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from typing import Optional


class StaticHookRegistration(HookRegistration):

    def __init__(self, plugin, hook: HookType, priority: int = 0, template: Optional[str] = None):
        super().__init__(plugin, hook, priority)
        self._template = template

    @property
    def template(self) -> Optional[str]:
        return self._template

    @template.setter
    def template(self, value: Optional[str]):
        self._template = value

    def __str__(self) -> str:
        return f"StaticHookRegistration(" \
               f"plugin='{self.plugin.get_id()}',\n" \
               f"hook='{self.hook}',\n" \
               f"priority='{self.priority}',\n" \
               f"template='{self.template}',\n" \
               f")"
    
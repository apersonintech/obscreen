from src.interface.ObPlugin import ObPlugin

from typing import List, Dict
from src.model.entity.Variable import Variable
from src.model.enum.VariableType import VariableType
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration


class GitUpdater(ObPlugin):

    def use_id(self):
        return 'git_updater'

    def use_title(self):
        return 'Git Updater'

    def use_variables(self) -> List[Variable]:
        return []

    def use_hooks_registrations(self) -> List[HookRegistration]:
        return [
            super().add_static_hook_registration(hook=HookType.H_SYSINFO_TOOLBAR_ACTIONS_START, priority=10),
        ]

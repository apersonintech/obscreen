from plugins.system.ObPlugin import ObPlugin

from typing import List, Dict
from src.model.Variable import Variable
from src.model.VariableType import VariableType
from src.model.HookType import HookType
from src.model.HookRegistration import HookRegistration


class FleetScreenRestart(ObPlugin):

    def use_id(self):
        return 'fleet_screen_restart'

    def use_title(self):
        return 'Fleet Screen Restart'

    def use_variables(self) -> List[Variable]:
        return []

    def use_hooks_registrations(self) -> List[HookRegistration]:
        return [
            super().set_hook_registration(hook=HookType.H_FLEET_SLIDESHOW_TOOLBAR_ACTIONS, priority=10)
        ]

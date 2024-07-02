from src.interface.ObPlugin import ObPlugin

from typing import List, Dict
from src.model.entity.Variable import Variable
from src.model.enum.VariableType import VariableType
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.util.utils import am_i_in_docker


class GitUpdater(ObPlugin):

    def use_id(self):
        return 'git_updater'

    def use_title(self):
        return self.translate('plugin_title')

    def use_description(self):
        return self.translate('plugin_description')

    def use_variables(self) -> List[Variable]:
        return []

    def use_hooks_registrations(self) -> List[HookRegistration]:
        return [
            super().add_functional_hook_registration(hook=HookType.H_SYSINFO_TOOLBAR_ACTIONS_START, priority=10, function=self.hook_update_button),
        ]

    def hook_update_button(self) -> str:
        return self.render_view('@update_button.jinja.html', am_i_in_docker=am_i_in_docker)

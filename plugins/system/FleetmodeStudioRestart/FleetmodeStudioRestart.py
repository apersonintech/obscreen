from src.interface.ObPlugin import ObPlugin

from typing import List, Dict
from src.model.entity.Variable import Variable
from src.model.enum.VariableType import VariableType
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration


class FleetmodeStudioRestart(ObPlugin):

    def use_id(self):
        return 'fleetmode_studio_restart'

    def use_title(self):
        return 'Fleetmode Studio Restart'

    def use_variables(self) -> List[Variable]:
        return [
    #         self.add_variable(
    #             name="foo",
    #             description="foo",
    #             type=VariableType.SELECT_SINGLE,
    #             value="foo",
    #             editable=True,
    #             selectables={"alpha": "Alpha", "beta": "Beta"}
    #         )
        ]

    def use_hooks_registrations(self) -> List[HookRegistration]:
        return [
            super().add_static_hook_registration(hook=HookType.H_FLEETMODE_SLIDESHOW_TOOLBAR_ACTIONS, priority=10),
            # super().add_functional_hook_registration(hook=HookType.H_FLEETMODE_SLIDESHOW_TOOLBAR_ACTIONS, priority=10, function=self.functional_foo),
        ]

    # def functional_foo(self) -> str:
    #     return 'functional_foo hook'
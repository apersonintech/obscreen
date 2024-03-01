import os
import logging
import inspect
import importlib

from plugins.system.ObPlugin import ObPlugin
from src.service.ModelStore import ModelStore
from src.manager.VariableManager import VariableManager
from src.model.VariableType import VariableType
from src.model.HookType import HookType
from src.model.HookRegistration import HookRegistration
from typing import List, Dict, Union


class PluginStore:

    FOLDER_PLUGINS_SYSTEM = 'plugins/system'
    FOLDER_PLUGINS_USER = 'plugins/user'
    DEFAULT_PLUGIN_ENABLED_VARIABLE = "enabled"

    def __init__(self, project_dir: str, model_store: ModelStore):
        self._project_dir = project_dir
        self._model_store = model_store
        self._hooks = self.pre_load_hooks()
        self._dead_variables_candidates = VariableManager.list_to_map(self._model_store.variable().get_by_prefix(ObPlugin.PLUGIN_PREFIX))
        self._system_plugins = self.find_plugins_in_directory(self.FOLDER_PLUGINS_SYSTEM)
        self._system_plugins = self.find_plugins_in_directory(self.FOLDER_PLUGINS_USER)
        self.post_load_hooks()
        self.clean_dead_variables()


    def map_hooks(self) -> Dict[HookType, List[HookRegistration]]:
        return self._hooks

    def find_plugins_in_directory(self, directory: str) -> list:
        plugins = []
        for root, dirs, files in os.walk('{}/{}'.format(self._project_dir, directory)):
            for file in files:
                if file.endswith(".py"):
                    module_name = file[:-3]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, ObPlugin) and obj is not ObPlugin:
                            plugin = obj(
                                directory=root,
                                model_store=self._model_store
                            )
                            plugins.append(plugin)
                            self.setup_plugin(plugin)

        return plugins

    def pre_load_hooks(self) -> Dict[HookType, List[HookRegistration]]:
        hooks = {}

        for hook in HookType:
            hooks[hook] = []

        return hooks

    def post_load_hooks(self) -> None:
        for hook_type in self._hooks:
            self._hooks[hook_type] = sorted(self._hooks[hook_type], key=lambda hook_reg: hook_reg.priority, reverse=True)

    def setup_plugin(self, plugin: ObPlugin) -> None:
        variables = plugin.use_variables() + [
            plugin.set_variable(
                name=self.DEFAULT_PLUGIN_ENABLED_VARIABLE,
                value=False,
                type=VariableType.BOOL,
                editable=True,
                description="Enable {} plugin".format(plugin.use_title())
            )
        ]

        if not self.is_plugin_enabled(plugin):
            return

        for variable in variables:
            if variable.name in self._dead_variables_candidates:
                del self._dead_variables_candidates[variable.name]

        hooks_registrations = plugin.use_hooks_registrations()

        for hook_registration in hooks_registrations:
            if hook_registration.hook not in self._hooks:
                logging.error("Hook {} does not exist".format(hook.name))
                continue

            hook_registration.template = "{}/views/{}.jinja.html".format(plugin.get_directory(), hook_registration.hook.value)
            self._hooks[hook_registration.hook].append(hook_registration)

        logging.info("Plugin {} loaded ({} var{} and {} hook) from {}".format(
            plugin.use_title(),
            len(variables),
            "s" if len(variables) > 1 else "",
            len(hooks_registrations),
            "s" if len(hooks_registrations) > 1 else "",
            plugin.get_directory()
        ))

    def clean_dead_variables(self) -> None:
        for variable_name, variable in self._dead_variables_candidates.items():
            logging.info("Removing dead plugin variable {}".format(variable_name))
            self._model_store.variable().delete(variable.id)

    def is_plugin_enabled(self, plugin: ObPlugin) -> bool:
        var = self._model_store.variable().get_one_by_name(plugin.get_plugin_variable_name(self.DEFAULT_PLUGIN_ENABLED_VARIABLE))
        return var.as_bool() if var else False
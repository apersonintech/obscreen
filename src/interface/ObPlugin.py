import abc

from flask import request, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Optional, List, Dict, Union
from src.model.entity.Variable import Variable
from src.model.enum.VariableType import VariableType
from src.model.enum.VariableUnit import VariableUnit
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.model.hook.StaticHookRegistration import StaticHookRegistration
from src.model.hook.FunctionalHookRegistration import FunctionalHookRegistration
from src.service.ModelStore import ModelStore
from src.service.TemplateRenderer import TemplateRenderer
from src.constant.WebDirConstant import WebDirConstant
from src.service.AliasFileSystemLoader import AliasFileSystemLoader



class ObPlugin(abc.ABC):

    PLUGIN_PREFIX = "plugin_"

    def __init__(self, project_dir: str, plugin_dir: str, model_store: ModelStore, template_renderer: TemplateRenderer):
        self._project_dir = project_dir
        self._plugin_dir = plugin_dir
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._rendering_env = self._init_rendering_env()

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
        return self._plugin_dir

    def get_rendering_env(self) -> Environment:
        return self._rendering_env

    def get_plugin_variable_prefix(self) -> str:
        return "{}{}".format(self.PLUGIN_PREFIX, self.use_id())

    def get_plugin_variable_name(self, name: str) -> str:
        return "{}_{}".format(self.get_plugin_variable_prefix(), name)

    def add_variable(self, name: str, value='', section: str = '', type: VariableType = VariableType.STRING, editable: bool = True, description: str = '', selectables: Optional[Dict[str, str]] = None, unit: Optional[VariableUnit] = None, refresh_player: bool = False) -> Variable:
        return self._model_store.variable().set_variable(
            name=self.get_plugin_variable_name(name),
            section=section,
            value=value,
            type=type,
            editable=editable,
            description=description,
            unit=unit,
            refresh_player=refresh_player,
            selectables=selectables if isinstance(selectables, dict) else None,
            plugin=self.use_id(),
        )

    def add_static_hook_registration(self, hook: HookType, priority: int = 0) -> StaticHookRegistration:
        return StaticHookRegistration(plugin=self, hook=hook, priority=priority)

    def add_functional_hook_registration(self, hook: HookType, priority: int = 0, function=None) -> FunctionalHookRegistration:
        return FunctionalHookRegistration(plugin=self, hook=hook, priority=priority, function=function)

    def _init_rendering_env(self) -> Environment:
        alias_paths = {
            "::": "{}/".format(WebDirConstant.FOLDER_TEMPLATES),
            "@": "{}/{}/".format(self._plugin_dir.replace(self._project_dir, ''), WebDirConstant.FOLDER_TEMPLATES)
        }

        env = Environment(
            loader=AliasFileSystemLoader(
                searchpath=self._project_dir,
                alias_paths=alias_paths
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )

        return env

    def render_view(self, template_file: str, **parameters: dict) -> str:
        template = self.get_rendering_env().get_template(template_file)

        return template.render(
            l=self._model_store.lang().map(),
            request=request,
            url_for=url_for,
            **parameters,
            **self._template_renderer.get_view_globals(),
        )

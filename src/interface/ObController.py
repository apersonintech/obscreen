import abc

from typing import Optional, List, Dict, Union
from src.service.TemplateRenderer import TemplateRenderer
from src.service.ModelStore import ModelStore
from src.interface.ObPlugin import ObPlugin


class ObController(abc.ABC):

    def __init__(self, app, auth_required, model_store: ModelStore, template_renderer: TemplateRenderer, plugin: Optional[ObPlugin] = None):
        self._app = app
        self._auth = auth_required
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._plugin = plugin
        self.register()

    @abc.abstractmethod
    def register(self) -> None:
        pass

    def plugin(self) -> ObPlugin:
        if not isinstance(self._plugin, ObPlugin):
            raise Error('No plugin for controller {}'.format(self.__class__.__name__))

        return self._plugin


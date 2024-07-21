import abc

from typing import Optional, List, Dict, Union
from src.service.TemplateRenderer import TemplateRenderer
from src.service.ModelStore import ModelStore
from src.interface.ObPlugin import ObPlugin


class ObController(abc.ABC):

    def __init__(self, kernel, web_server, app, auth_required, model_store: ModelStore, template_renderer: TemplateRenderer, plugin: Optional[ObPlugin] = None):
        self._kernel = kernel
        self._web_server = web_server
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

    def get_template_folder(self):
        return self._web_server.get_template_folder()

    def get_web_folder(self):
        return self._web_server.get_web_folder()

    def reload_web_server(self):
        self._web_server.reload()

    def reload_lang(self, lang: str):
        self._kernel.reload_lang(lang)

    def t(self, token) -> Union[Dict, str]:
        return self._model_store.lang().translate(token)

    def get_external_storage_server(self):
        return self._kernel.external_storage_server

import sys
import logging
import signal
import threading

from src.service.ModelStore import ModelStore
from src.service.PluginStore import PluginStore
from src.service.TemplateRenderer import TemplateRenderer
from src.service.WebServer import WebServer
from src.model.enum.HookType import HookType


class Application:

    def __init__(self, project_dir: str):
        self._project_dir = project_dir
        self._stop_event = threading.Event()
        self._model_store = ModelStore(self.get_plugins)
        self._template_renderer = TemplateRenderer(project_dir=project_dir, model_store=self._model_store, render_hook=self.render_hook)
        self._web_server = WebServer(project_dir=project_dir, model_store=self._model_store, template_renderer=self._template_renderer)

        logging.info("[obscreen] Starting application v{}...".format(self.get_version()))
        self._plugin_store = PluginStore(project_dir=project_dir, model_store=self._model_store, template_renderer=self._template_renderer, web_server=self._web_server)
        signal.signal(signal.SIGINT, self.signal_handler)

    def start(self) -> None:
        self._web_server.run()

    def signal_handler(self, signal, frame) -> None:
        logging.info("Shutting down...")
        self._model_store.database().close()
        self._stop_event.set()
        sys.exit(0)

    def render_hook(self, hook: HookType) -> str:
        return self._template_renderer.render_hooks(self._plugin_store.map_hooks()[hook])

    def get_plugins(self):
        return self._plugin_store.map_plugins()

    @staticmethod
    def get_name() -> str:
        return 'obscreen-studio'

    @staticmethod
    def get_version() -> str:
        with open("version.txt", 'r') as file:
            return file.read().strip()

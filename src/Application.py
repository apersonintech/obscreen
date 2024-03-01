import sys
import logging
import signal
import threading

from src.service.ModelManager import ModelManager
from src.service.WebServer import WebServer


class Application:

    def __init__(self, project_dir: str):
        self._project_dir = project_dir
        self._stop_event = threading.Event()
        self._model_manager = ModelManager()
        self._web_server = WebServer(project_dir=project_dir, model_manager=self._model_manager)

        signal.signal(signal.SIGINT, self.signal_handler)

    def start(self) -> None:
        self._web_server.run()

    def signal_handler(self, signal, frame) -> None:
        logging.info("Shutting down...")
        self._stop_event.set()
        sys.exit(0)



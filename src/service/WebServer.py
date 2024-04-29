import os
import time

from flask import Flask, send_from_directory
from src.service.ModelStore import ModelStore
from src.service.TemplateRenderer import TemplateRenderer
from src.controller.PlayerController import PlayerController
from src.controller.SlideshowController import SlideshowController
from src.controller.FleetController import FleetController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController
from src.constant.WebDirConstant import WebDirConstant


class WebServer:

    MAX_UPLOADS = 16 * 1024 * 1024

    def __init__(self, project_dir: str, model_store: ModelStore, template_renderer: TemplateRenderer):
        self._project_dir = project_dir
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._debug = self._model_store.config().map().get('debug')
        self.setup()

    def run(self) -> None:
        self._app.run(
            host=self._model_store.config().map().get('bind'),
            port=self._model_store.config().map().get('port'),
            debug=self._debug
        )

    def setup(self) -> None:
        self._setup_flask_app()
        self._setup_web_globals()
        self._setup_web_extensions()
        self._setup_web_errors()
        self._setup_web_controllers()

    def get_app(self):
        return self._app

    def _get_template_folder(self) -> str:
        return "{}/{}".format(self._project_dir, WebDirConstant.FOLDER_TEMPLATES)

    def _get_static_folder(self) -> str:
        return "{}/{}".format(self._project_dir, WebDirConstant.FOLDER_STATIC)

    def _setup_flask_app(self) -> None:
        self._app = Flask(
            __name__,
            template_folder=self._get_template_folder(),
            static_folder=self._get_static_folder(),
        )

        self._app.config['UPLOAD_FOLDER'] = "{}/{}".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_UPLOADS)
        self._app.config['MAX_CONTENT_LENGTH'] = self.MAX_UPLOADS

        if self._debug:
            self._app.config['TEMPLATES_AUTO_RELOAD'] = True

    def _setup_web_controllers(self) -> None:
        PlayerController(self._app, self._model_store, self._template_renderer)
        SlideshowController(self._app, self._model_store, self._template_renderer)
        SettingsController(self._app, self._model_store, self._template_renderer)
        SysinfoController(self._app, self._model_store, self._template_renderer)

        if self._model_store.variable().map().get('fleet_enabled').as_bool():
            FleetController(self._app, self._model_store, self._template_renderer)

    def _setup_web_globals(self) -> None:
        @self._app.context_processor
        def inject_global_vars() -> dict:
            return self._template_renderer.get_view_globals()

    def _setup_web_extensions(self) -> None:
        @self._app.template_filter('ctime')
        def time_ctime(s):
            return time.ctime(s)

    def _setup_web_errors(self) -> None:
        @self._app.errorhandler(404)
        def not_found(e):
            return send_from_directory(self._get_template_folder(), 'core/error404.html'), 404

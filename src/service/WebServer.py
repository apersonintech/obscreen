import os
import time

from flask import Flask, send_from_directory
from src.service.ModelManager import ModelManager
from src.controller.PlayerController import PlayerController
from src.controller.SlideshowController import SlideshowController
from src.controller.FleetController import FleetController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController


class WebServer:

    FOLDER_TEMPLATES = "views"
    FOLDER_STATIC = "data"
    FOLDER_STATIC_WEB_UPLOADS = "uploads"
    FOLDER_STATIC_WEB_ASSETS = "www"
    MAX_UPLOADS = 16 * 1024 * 1024

    def __init__(self, project_dir: str, model_manager: ModelManager):
        self._project_dir = project_dir
        self._model_manager = model_manager
        self._debug = self._model_manager.config().map().get('debug')
        self.setup()

    def run(self) -> None:
        self._app.run(
            host=self._model_manager.variable().map().get('bind').as_string(),
            port=self._model_manager.variable().map().get('port').as_int(),
            debug=self._debug
        )

    def setup(self) -> None:
        self._setup_flask_app()
        self._setup_view_globals()
        self._setup_view_extensions()
        self._setup_view_errors()
        self._setup_view_controllers()

    def _get_template_folder(self) -> str:
        return "{}/{}".format(self._project_dir, self.FOLDER_TEMPLATES)

    def _get_static_folder(self) -> str:
        return "{}/{}".format(self._project_dir, self.FOLDER_STATIC)

    def _setup_flask_app(self) -> None:
        self._app = Flask(
            __name__,
            template_folder=self._get_template_folder(),
            static_folder=self._get_static_folder(),
        )

        self._app.config['UPLOAD_FOLDER'] = "{}/{}".format(self.FOLDER_STATIC, self.FOLDER_STATIC_WEB_UPLOADS)
        self._app.config['MAX_CONTENT_LENGTH'] = self.MAX_UPLOADS

        if self._debug:
            self._app.config['TEMPLATES_AUTO_RELOAD'] = True

    def _setup_view_controllers(self) -> None:
        PlayerController(self._app, self._model_manager)
        SlideshowController(self._app, self._model_manager)
        SettingsController(self._app, self._model_manager)
        SysinfoController(self._app, self._model_manager)

        if self._model_manager.variable().map().get('fleet_enabled').as_bool():
            FleetController(self._app, self._model_manager)

    def _setup_view_globals(self) -> None:
        @self._app.context_processor
        def inject_global_vars():
            return dict(
                FLEET_ENABLED=self._model_manager.variable().map().get('fleet_enabled').as_bool(),
                LANG=self._model_manager.variable().map().get('lang').as_string(),
                STATIC_PREFIX="/{}/{}/".format(self.FOLDER_STATIC, self.FOLDER_STATIC_WEB_ASSETS)
            )

    def _setup_view_extensions(self) -> None:
        @self._app.template_filter('ctime')
        def time_ctime(s):
            return time.ctime(s)

    def _setup_view_errors(self) -> None:
        @self._app.errorhandler(404)
        def not_found(e):
            return send_from_directory(self._get_template_folder(), 'core/error404.html'), 404

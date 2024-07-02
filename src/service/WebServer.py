import os
import time
from waitress import serve

from flask import Flask, send_from_directory, redirect, url_for
from flask_login import LoginManager, current_user

from src.manager.UserManager import UserManager
from src.service.ModelStore import ModelStore
from src.service.TemplateRenderer import TemplateRenderer
from src.controller.PlayerController import PlayerController
from src.controller.SlideController import SlideController
from src.controller.ContentController import ContentController
from src.controller.FleetNodePlayerController import FleetNodePlayerController
from src.controller.FleetNodePlayerGroupController import FleetNodePlayerGroupController
from src.controller.PlaylistController import PlaylistController
from src.controller.AuthController import AuthController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController
from src.controller.CoreController import CoreController
from src.constant.WebDirConstant import WebDirConstant


class WebServer:

    def __init__(self, kernel, model_store: ModelStore, template_renderer: TemplateRenderer):
        self._app = None
        self._auth_enabled = False
        self._login_manager = None
        self._kernel = kernel
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._debug = self._model_store.config().map().get('debug')
        self.setup()

    def run(self) -> None:
        serve(
            self._app,
            host=self._model_store.config().map().get('bind'),
            port=self._model_store.config().map().get('port')
        )

    def reload(self) -> None:
        self.setup()

    def setup(self) -> None:
        self._setup_flask_app()
        self._setup_web_globals()
        self._setup_web_errors()
        self._setup_web_controllers()

    def get_app(self):
        return self._app

    def get_template_folder(self) -> str:
        return "{}/{}".format(self._kernel.get_project_dir(), WebDirConstant.FOLDER_TEMPLATES)

    def get_static_folder(self) -> str:
        return "{}/{}".format(self._kernel.get_project_dir(), WebDirConstant.FOLDER_STATIC)

    def get_web_folder(self) -> str:
        return "{}/{}/{}".format(self._kernel.get_project_dir(), WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS)

    def _setup_flask_app(self) -> None:
        self._app = Flask(
            __name__,
            template_folder=self.get_template_folder(),
            static_folder=self.get_static_folder(),
        )

        self._app.config['UPLOAD_FOLDER'] = "{}/{}".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_UPLOADS)
        self._app.config['MAX_CONTENT_LENGTH'] = self._model_store.variable().map().get('slide_upload_limit').as_int() * 1024 * 1024

        self._setup_flask_login()

        if self._debug:
            self._app.config['TEMPLATES_AUTO_RELOAD'] = True

    def _setup_flask_login(self):
        self._app.config['SECRET_KEY'] = self._model_store.config().map().get('secret_key')
        self._login_manager = LoginManager()
        self._login_manager.init_app(self._app)
        self._login_manager.login_view = 'login'

        @self._login_manager.user_loader
        def load_user(user_id):
            return self._model_store.user().get(user_id)

    def auth_required(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('auth_enabled').as_bool():
                return f(*args, **kwargs)

            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            return f(*args, **kwargs)

        return decorated_function

    def _setup_web_controllers(self) -> None:
        CoreController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        PlayerController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SlideController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        ContentController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SettingsController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SysinfoController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        FleetNodePlayerController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        FleetNodePlayerGroupController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        PlaylistController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        AuthController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)

    def _setup_web_globals(self) -> None:
        @self._app.context_processor
        def inject_global_vars() -> dict:
            return self._template_renderer.get_view_globals()

    def _setup_web_errors(self) -> None:
        @self._app.errorhandler(404)
        def not_found(e):
            return send_from_directory(self.get_template_folder(), 'core/error404.html'), 404


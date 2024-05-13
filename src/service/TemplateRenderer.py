import os

from flask import Flask, send_from_directory, Markup
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.service.ModelStore import ModelStore
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.model.hook.StaticHookRegistration import StaticHookRegistration
from src.model.hook.FunctionalHookRegistration import FunctionalHookRegistration
from src.constant.WebDirConstant import WebDirConstant
from src.utils import get_safe_cron_descriptor, is_validate_cron_date_time


class TemplateRenderer:

    def __init__(self, project_dir: str, model_store: ModelStore, render_hook):
        self._project_dir = project_dir
        self._model_store = model_store
        self._render_hook = render_hook

    def cron_descriptor(self, expression: str, use_24hour_time_format=True) -> str:
        return get_safe_cron_descriptor(expression, use_24hour_time_format, self._model_store.lang().get_lang(local_with_country=True))

    def get_view_globals(self) -> dict:
        globals = dict(
            STATIC_PREFIX="/{}/{}/".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS),
            FLEET_ENABLED=self._model_store.variable().map().get('fleet_enabled').as_bool(),
            AUTH_ENABLED=self._model_store.variable().map().get('auth_enabled').as_bool(),
            track_created=self._model_store.user().track_user_created,
            track_updated=self._model_store.user().track_user_updated,
            VERSION=self._model_store.config().map().get('version'),
            LANG=self._model_store.variable().map().get('lang').as_string(),
            HOOK=self._render_hook,
            cron_descriptor=self.cron_descriptor,
            is_validate_cron_date_time=is_validate_cron_date_time,
            l=self._model_store.lang().map(),
            t=self._model_store.lang().translate,
        )

        for hook in HookType:
            globals[hook.name] = hook

        return globals

    def render_hooks(self, hooks_registrations: List[HookRegistration]) -> str:
        content = []

        for hook_registration in hooks_registrations:
            if isinstance(hook_registration, StaticHookRegistration):
                template = hook_registration.plugin.get_rendering_env().get_template("@{}/{}".format(
                    WebDirConstant.FOLDER_PLUGIN_HOOK,
                    os.path.basename(hook_registration.template)
                ))
                content.append(template.render(
                    **self.get_view_globals()
                ))
            elif isinstance(hook_registration, FunctionalHookRegistration):
                content.append(hook_registration.function())

        return Markup("".join(content))

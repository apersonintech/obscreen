import os
import json

from flask import Flask, send_from_directory, Markup, url_for
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.service.ModelStore import ModelStore
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.model.hook.StaticHookRegistration import StaticHookRegistration
from src.model.hook.FunctionalHookRegistration import FunctionalHookRegistration
from src.constant.WebDirConstant import WebDirConstant
from src.util.utils import get_safe_cron_descriptor, \
    is_cron_calendar_moment, \
    is_cron_in_day_moment, \
    is_cron_in_week_moment, \
    seconds_to_hhmmss, am_i_in_docker, \
    truncate, merge_dicts, dictsort


class TemplateRenderer:

    def __init__(self, kernel, model_store: ModelStore, render_hook):
        self._kernel = kernel
        self._model_store = model_store
        self._render_hook = render_hook

    def cron_descriptor(self, expression: str, use_24hour_time_format=True) -> str:
        return get_safe_cron_descriptor(expression, use_24hour_time_format, self._model_store.lang().get_lang(local_with_country=True))

    def get_view_globals(self) -> dict:
        globals = dict(
            STATIC_PREFIX="/{}/{}/".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS),
            SECRET_KEY=self._model_store.config().map().get('secret_key'),
            FLEET_PLAYER_ENABLED=self._model_store.variable().map().get('fleet_player_enabled').as_bool(),
            DARK_MODE=self._model_store.variable().map().get('dark_mode').as_bool(),
            AUTH_ENABLED=self._model_store.variable().map().get('auth_enabled').as_bool(),
            last_pillmenu_slideshow=self._model_store.variable().map().get('last_pillmenu_slideshow').as_string(),
            last_pillmenu_configuration=self._model_store.variable().map().get('last_pillmenu_configuration').as_string(),
            last_pillmenu_fleet=self._model_store.variable().map().get('last_pillmenu_fleet').as_string(),
            last_pillmenu_security=self._model_store.variable().map().get('last_pillmenu_security').as_string(),
            track_created=self._model_store.user().track_user_created,
            track_updated=self._model_store.user().track_user_updated,
            PORT=self._model_store.config().map().get('port'),
            VERSION=self._model_store.config().map().get('version'),
            LANG=self._model_store.variable().map().get('lang').as_string(),
            HOOK=self._render_hook,
            cron_descriptor=self.cron_descriptor,
            str=str,
            seconds_to_hhmmss=seconds_to_hhmmss,
            is_cron_calendar_moment=is_cron_calendar_moment,
            is_cron_in_day_moment=is_cron_in_day_moment,
            json_dumps=json.dumps,
            merge_dicts=merge_dicts,
            dictsort=dictsort,
            truncate=truncate,
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
                    **self.get_view_globals(),
                    url_for=url_for
                ))
            elif isinstance(hook_registration, FunctionalHookRegistration):
                content.append(hook_registration.function())

        return Markup("".join(content))

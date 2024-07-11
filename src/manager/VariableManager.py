import json
import time
from typing import Dict, Optional, List, Tuple, Union

from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.model.entity.Variable import Variable
from src.model.entity.Selectable import Selectable
from src.model.enum.FolderEntity import FOLDER_ROOT_PATH
from src.model.enum.ApplicationLanguage import ApplicationLanguage
from src.model.enum.VariableType import VariableType
from src.model.enum.VariableUnit import VariableUnit
from src.model.enum.VariableSection import VariableSection
from src.model.enum.AnimationEntranceEffect import AnimationEntranceEffect
from src.model.enum.AnimationExitEffect import AnimationExitEffect
from src.model.enum.AnimationSpeed import AnimationSpeed
from src.util.utils import get_keys, enum_to_str, enum_to_dict

SELECTABLE_BOOLEAN = {"1": "✅", "0": "❌"}


class VariableManager:

    TABLE_NAME = "settings"
    TABLE_MODEL = [
        "description TEXT",
        "description_edition TEXT",
        "editable INTEGER",
        "name CHAR(255)",
        "section CHAR(255)",
        "plugin CHAR(255)",
        "selectables TEXT",
        "type CHAR(255)",
        "unit CHAR(255)",
        "refresh_player INTEGER",
        "value TEXT"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager):
        self._lang_manager = lang_manager
        self._user_manager = user_manager
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)
        self._var_map = {}
        self.reload()

    def t(self, token) -> Union[Dict, str]:
        return self._lang_manager.translate(token)

    def set_variable(self, name: str, value, type: VariableType, editable: bool, description: str, description_edition: str = '', plugin: Optional[None] = None, selectables: Optional[Dict[str, str]] = None, unit: Optional[VariableUnit] = None, section: str = '', refresh_player: bool = False) -> Variable:
        if isinstance(value, bool) and value:
            value = '1'
        elif isinstance(value, bool) and not value:
            value = '0'

        if type == VariableType.BOOL:
            selectables = SELECTABLE_BOOLEAN

        default_var = {
            "name": name,
            "section": section,
            "value": value,
            "type": type.value,
            "editable": editable,
            "refresh_player": refresh_player,
            "description": description,
            "description_edition": description_edition,
            "plugin": plugin,
            "unit": unit.value if unit else None,
            "selectables": ([{"key": key, "label": label} for key, label in selectables.items()]) if isinstance(selectables, dict) else None
        }
        variable = self.get_one_by_name(default_var['name'])

        if not variable:
            self.add_form(default_var)
            variable = self.get_one_by_name(default_var['name'])
        else:
            same_selectables_keys = get_keys(default_var, 'selectables', 'key') == get_keys(variable, 'selectables', 'key')
            same_selectables_label = get_keys(default_var, 'selectables', 'label') == get_keys(variable, 'selectables', 'label')

            if variable.description != default_var['description']:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"description": default_var['description']})

            if variable.description_edition != default_var['description_edition']:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"description_edition": default_var['description_edition']})

            if variable.unit != default_var['unit']:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"unit": default_var['unit']})

            if variable.section != default_var['section']:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"section": default_var['section']})

            if variable.refresh_player != default_var['refresh_player']:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"refresh_player": default_var['refresh_player']})

            if not same_selectables_keys or not same_selectables_label:
                self._db.update_by_id(self.TABLE_NAME, variable.id, {"selectables": default_var['selectables']})

        if variable.name == 'last_restart':
            self._db.update_by_id(self.TABLE_NAME, variable.id, {"value": time.time()})

        return variable

    def reload(self) -> None:
        default_vars = [
            # Editable (Customizable settings)

            ### General
            {"name": "lang", "section": self.t(VariableSection.GENERAL), "value": "en", "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_lang'), "selectables": self.t(ApplicationLanguage), "refresh_player": False},
            {"name": "external_url", "section": self.t(VariableSection.GENERAL), "value": "", "type": VariableType.STRING, "editable": True, "description": self.t('settings_variable_desc_external_url'), "refresh_player": False},
            {"name": "slide_upload_limit", "section": self.t(VariableSection.GENERAL), "value": 32, "unit": VariableUnit.MEGABYTE,  "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_slide_upload_limit'), "refresh_player": False},

            ### Player Options
            {"name": "default_slide_duration", "section": self.t(VariableSection.PLAYER_OPTIONS), "value": 3, "unit": VariableUnit.SECOND, "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_default_slide_duration'), "refresh_player": False},
            {"name": "default_slide_time_with_seconds", "section": self.t(VariableSection.PLAYER_OPTIONS), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_default_slide_time_with_seconds'), "refresh_player": False},
            {"name": "polling_interval", "section": self.t(VariableSection.PLAYER_OPTIONS), "value": 5, "unit": VariableUnit.SECOND, "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_polling_interval'), "refresh_player": True},

            ### Player Animation
            {"name": "slide_animation_enabled", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_slide_animation_enabled'), "refresh_player": True},
            {"name": "slide_animation_entrance_effect", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationEntranceEffect.FADE_IN.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_entrance_effect'), "selectables": enum_to_dict(AnimationEntranceEffect), "refresh_player": True},
            {"name": "slide_animation_exit_effect", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationExitEffect.NONE.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_exit_effect'), "selectables": enum_to_dict(AnimationExitEffect), "refresh_player": True},
            {"name": "slide_animation_speed", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationSpeed.NORMAL.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_speed'), "selectables": self.t(AnimationSpeed), "refresh_player": True},

            ### Playlists
            {"name": "playlist_enabled", "section": self.t(VariableSection.PLAYLIST), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_playlist_enabled'), "refresh_player": False},
            {"name": "playlist_default_time_sync", "section": self.t(VariableSection.PLAYLIST), "value": True, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_playlist_default_time_sync'), "refresh_player": True},

            ### Fleet Management
            {"name": "fleet_player_enabled", "section": self.t(VariableSection.FLEET), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_fleet_player_enabled'), "description_edition": self.t('settings_variable_desc_edition_fleet_player_enabled'), "refresh_player": False},

            ### Security
            {"name": "auth_enabled", "section": self.t(VariableSection.SECURITY), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_auth_enabled'), "description_edition": self.t('settings_variable_desc_edition_auth_enabled'), "refresh_player": False},

            # Not editable (System information)
            {"name": "last_folder_content", "value": FOLDER_ROOT_PATH, "type": VariableType.STRING, "editable": False, "description": self.t('settings_variable_desc_ro_last_folder_content')},
            {"name": "last_folder_node_player", "value": FOLDER_ROOT_PATH, "type": VariableType.STRING, "editable": False, "description": self.t('settings_variable_desc_ro_last_folder_node_player')},
            {"name": "last_restart", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_editable')},
            {"name": "last_slide_update", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_last_slide_update')},
            {"name": "refresh_player_request", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_refresh_player_request')},
        ]

        for default_var in default_vars:
            self.set_variable(**default_var)

        self._var_map = self.prepare_map()

    def map(self) -> dict:
        return self._var_map

    def prepare_map(self) -> Dict[str, Variable]:
        return self.list_to_map(self.get_all())

    @staticmethod
    def list_to_map(list: List[Variable]) -> Dict[str, Variable]:
        var_map = {}

        for var in list:
            var_map[var.name] = var

        return var_map

    def hydrate_object(self, raw_variable: dict, id: Optional[int] = None) -> Variable:
        if id:
            raw_variable['id'] = id

        if 'selectables' in raw_variable and raw_variable['selectables']:
            raw_variable['selectables'] = [Selectable(**selectable) for selectable in json.loads(raw_variable['selectables'])]

        return Variable(**raw_variable)

    def hydrate_list(self, raw_variables: list) -> List[Variable]:
        return [self.hydrate_object(raw_variable) for raw_variable in raw_variables]

    def get(self, id: int) -> Optional[Variable]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[Variable]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_by_prefix(self, prefix: str) -> List[Variable]:
        return self.get_by(query="name like '{}%'".format(prefix))

    def get_by_plugin(self, plugin: str) -> List[Variable]:
        return self.get_by(query="plugin = '{}'".format(plugin))

    def get_one_by_name(self, name: str) -> Optional[Variable]:
        return self.get_one_by("name = '{}'".format(name))

    def get_one_by(self, query) -> Optional[Variable]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self) -> List[Variable]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME))

    def get_editable_variables(self, plugin: bool = True, sort: Optional[str] = None) -> List[Variable]:
        query = "plugin is null and editable = 1" if not plugin else "plugin is not null and length(plugin) > 0 and editable = 1"
        return self.get_by(query=query, sort=sort)

    def get_readonly_variables(self) -> List[Variable]:
        return self.get_by(query="editable = 0", sort="name")

    def update_form(self, id: int, value: Union[int, bool, str]) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"value": value})
        var = self.get_one_by("id = {}".format(id))
        self._var_map[var.name] = var

    def update_by_name(self, name: str, value) -> Optional[Variable]:
        self._db.update_by_query(self.TABLE_NAME, query="name = '{}'".format(name), values={"value": value})
        var = self.get_one_by_name(name)
        self._var_map[name] = var

    def add_form(self, variable: Union[Variable, Dict]) -> None:
        form = variable

        if not isinstance(variable, dict):
            form = variable.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, form)

    def delete(self, id: int) -> None:
        self._db.delete_by_id(self.TABLE_NAME, id)

    def to_dict(self, variables: List[Variable]) -> List[Dict]:
        return [variable.to_dict() for variable in variables]

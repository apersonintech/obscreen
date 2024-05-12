import time
from typing import Dict, Optional, List, Tuple, Union
from pysondb.errors import IdDoesNotExistError

from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.service.ModelManager import ModelManager
from src.model.entity.Variable import Variable
from src.model.entity.Selectable import Selectable
from src.model.enum.ApplicationLanguage import ApplicationLanguage
from src.model.enum.VariableType import VariableType
from src.model.enum.VariableUnit import VariableUnit
from src.model.enum.VariableSection import VariableSection
from src.model.enum.AnimationEntranceEffect import AnimationEntranceEffect
from src.model.enum.AnimationExitEffect import AnimationExitEffect
from src.model.enum.AnimationSpeed import AnimationSpeed
from src.utils import get_keys, enum_to_str, enum_to_dict

SELECTABLE_BOOLEAN = {"1": "✅", "0": "❌"}


class VariableManager(ModelManager):

    TABLE_NAME = "settings"
    TABLE_MODEL = [
        "description",
        "description_edition",
        "editable",
        "name",
        "section",
        "plugin",
        "selectables",
        "type",
        "unit",
        "refresh_player",
        "value"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager):
        super().__init__(lang_manager, database_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)
        self._var_map = {}
        self.reload()

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
                self._db.update_by_id(variable.id, {"description": default_var['description']})

            if variable.description_edition != default_var['description_edition']:
                self._db.update_by_id(variable.id, {"description_edition": default_var['description_edition']})

            if variable.unit != default_var['unit']:
                self._db.update_by_id(variable.id, {"unit": default_var['unit']})

            if variable.section != default_var['section']:
                self._db.update_by_id(variable.id, {"section": default_var['section']})

            if variable.refresh_player != default_var['refresh_player']:
                self._db.update_by_id(variable.id, {"refresh_player": default_var['refresh_player']})

            if not same_selectables_keys or not same_selectables_label:
                self._db.update_by_id(variable.id, {"selectables": default_var['selectables']})

        if variable.name == 'last_restart':
            self._db.update_by_id(variable.id, {"value": time.time()})

        return variable

    def reload(self) -> None:
        default_vars = [
            # Editable (Customizable settings)

            ### General
            {"name": "lang", "section": self.t(VariableSection.GENERAL), "value": "en", "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_lang'), "selectables": self.t(ApplicationLanguage), "refresh_player": False},
            {"name": "auth_enabled", "section": self.t(VariableSection.GENERAL), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_auth_enabled'), "description_edition": self.t('settings_variable_desc_edition_auth_enabled'), "refresh_player": False},
            {"name": "fleet_enabled", "section": self.t(VariableSection.GENERAL), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_fleet_enabled'), "refresh_player": False},
            {"name": "external_url", "section": self.t(VariableSection.GENERAL), "value": "", "type": VariableType.STRING, "editable": True, "description": self.t('settings_variable_desc_external_url'), "refresh_player": False},
            {"name": "slide_upload_limit", "section": self.t(VariableSection.GENERAL), "value": 32, "unit": VariableUnit.MEGABYTE,  "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_slide_upload_limit'), "refresh_player": False},

            ### Player Options
            {"name": "default_slide_duration", "section": self.t(VariableSection.PLAYER_OPTIONS), "value": 3, "unit": VariableUnit.SECOND, "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_default_slide_duration'), "refresh_player": False},
            {"name": "polling_interval", "section": self.t(VariableSection.PLAYER_OPTIONS), "value": 5, "unit": VariableUnit.SECOND, "type": VariableType.INT, "editable": True, "description": self.t('settings_variable_desc_polling_interval'), "refresh_player": True},

             ### Player Animation
            {"name": "slide_animation_enabled", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": False, "type": VariableType.BOOL, "editable": True, "description": self.t('settings_variable_desc_slide_animation_enabled'), "refresh_player": True},
            {"name": "slide_animation_entrance_effect", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationEntranceEffect.FADE_IN.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_entrance_effect'), "selectables": enum_to_dict(AnimationEntranceEffect), "refresh_player": True},
            {"name": "slide_animation_exit_effect", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationExitEffect.NONE.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_exit_effect'), "selectables": enum_to_dict(AnimationExitEffect), "refresh_player": True},
            {"name": "slide_animation_speed", "section": self.t(VariableSection.PLAYER_ANIMATION), "value": AnimationSpeed.NORMAL.value, "type": VariableType.SELECT_SINGLE, "editable": True, "description": self.t('settings_variable_desc_slide_animation_speed'), "selectables": self.t(AnimationSpeed), "refresh_player": True},

            # Not editable (System information)
            {"name": "last_restart", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_editable')},
            {"name": "last_slide_update", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_last_slide_update')},
            {"name": "refresh_player_request", "value": time.time(), "type": VariableType.TIMESTAMP, "editable": False, "description": self.t('settings_variable_desc_ro_refresh_player_request')},
        ]

        for default_var in default_vars:
            self.set_variable(**default_var)

        self._var_map = self.prepare_variable_map()

    def map(self) -> dict:
        return self._var_map

    def prepare_variable_map(self) -> Dict[str, Variable]:
        return self.list_to_map(self.get_all())

    @staticmethod
    def list_to_map(list: List[Variable]) -> Dict[str, Variable]:
        var_map = {}

        for var in list:
            var_map[var.name] = var

        return var_map

    @staticmethod
    def hydrate_object(raw_variable: dict, id: Optional[str] = None) -> Variable:
        if id:
            raw_variable['id'] = id

        if 'selectables' in raw_variable and raw_variable['selectables']:
            raw_variable['selectables'] = [Selectable(**selectable) for selectable in raw_variable['selectables']]

        return Variable(**raw_variable)

    @staticmethod
    def hydrate_dict(raw_variables: dict) -> List[Variable]:
        return [VariableManager.hydrate_object(raw_variable, raw_id) for raw_id, raw_variable in raw_variables.items()]

    @staticmethod
    def hydrate_list(raw_variables: list) -> List[Variable]:
        return [VariableManager.hydrate_object(raw_variable) for raw_variable in raw_variables]

    def get(self, id: str) -> Optional[Variable]:
        try:
            return self.hydrate_object(self._db.get_by_id(id), id)
        except IdDoesNotExistError:
            return None

    def get_by(self, query) -> List[Variable]:
        return self.hydrate_dict(self._db.get_by_query(query=query))

    def get_by_prefix(self, prefix: str) -> List[Variable]:
        return self.hydrate_dict(self._db.get_by_query(query=lambda v: v['name'].startswith(prefix)))

    def get_by_plugin(self, plugin: str) -> List[Variable]:
        return self.hydrate_dict(self._db.get_by_query(query=lambda v: v['plugin'] == plugin))

    def get_one_by_name(self, name: str) -> Optional[Variable]:
        return self.get_one_by(query=lambda v: v['name'] == name)

    def get_one_by(self, query) -> Optional[Variable]:
        object = self._db.get_by_query(query=query)
        variables = self.hydrate_dict(object)
        if len(variables) == 1:
            return variables[0]
        elif len(variables) > 1:
            raise Error("More than one result for query")
        return None

    def get_all(self) -> List[Variable]:
        raw_variables = self._db.get_all()

        if isinstance(raw_variables, dict):
            return VariableManager.hydrate_dict(raw_variables)

        return VariableManager.hydrate_list(raw_variables)

    def get_editable_variables(self, plugin: bool = True, sort: Optional[str] = None) -> List[Variable]:
        query = lambda v: (not plugin and not isinstance(v['plugin'], str)) or (plugin and isinstance(v['plugin'], str))
        variables = [variable for variable in self.get_by(query=query) if variable.editable]
        if sort is not None and sort:
            return sorted(variables, key=lambda x: getattr(x, sort))
        return variables

    def get_readonly_variables(self) -> List[Variable]:
        return [variable for variable in self.get_all() if not variable.editable]

    def update_form(self, id: str, value: Union[int, bool, str]) -> None:
        var_dict = self._db.update_by_id(id, {"value": value})
        var = self.hydrate_object(var_dict, id)
        self._var_map[var.name] = var

    def update_by_name(self, name: str, value) -> Optional[Variable]:
        [var_id] = self._db.update_by_query(query=lambda v: v['name'] == name, new_data={"value": value})
        var_dict = self._db.get_by_id(var_id)
        var = self.hydrate_object(var_dict, id)
        self._var_map[name] = var

    def add_form(self, variable: Union[Variable, Dict]) -> None:
        form = variable

        if not isinstance(variable, dict):
            form = variable.to_dict()
            del form['id']

        self._db.add(form)

    def delete(self, id: str) -> None:
        self._db.delete_by_id(id)

    def to_dict(self, variables: List[Variable]) -> List[Dict]:
        return [variable.to_dict() for variable in variables]

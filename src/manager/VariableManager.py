from typing import Dict, Optional, List, Tuple, Union
from src.model.Variable import Variable
from src.model.VariableType import VariableType
from pysondb import PysonDB
from pysondb.errors import IdDoesNotExistError
import time


class VariableManager:

    DB_FILE = "data/db/settings.json"

    def __init__(self):
        self._db = PysonDB(self.DB_FILE)
        self.init()

    def init(self, lang_dict: Optional[Dict] = None) -> None:
        default_vars = [
            {"name": "port", "value": 5000, "type": VariableType.INT.value, "editable": True, "description": lang_dict['settings_variable_help_port'] if lang_dict else ""},
            {"name": "bind", "value": '0.0.0.0', "type": VariableType.STRING.value, "editable": True, "description": lang_dict['settings_variable_help_bind'] if lang_dict else ""},
            {"name": "lang", "value": "en", "type": VariableType.STRING.value, "editable": True, "description": lang_dict['settings_variable_help_lang'] if lang_dict else ""},
            {"name": "fleet_enabled", "value": "0", "type": VariableType.BOOL.value, "editable": True, "description": lang_dict['settings_variable_help_fleet_enabled'] if lang_dict else ""},
            {"name": "external_url", "value": "", "type": VariableType.STRING.value, "editable": True, "description": lang_dict['settings_variable_help_external_url'] if lang_dict else ""},
            {"name": "last_restart", "value": time.time(), "type": VariableType.TIMESTAMP.value, "editable": False, "description": lang_dict['settings_variable_help_ro_editable'] if lang_dict else ""},
            {"name": "last_slide_update", "value": time.time(), "type": VariableType.TIMESTAMP.value, "editable": False, "description": lang_dict['settings_variable_help_ro_last_slide_update'] if lang_dict else ""},
        ]

        for default_var in default_vars:
            variable = self.get_one_by_name(default_var['name'])

            if not variable:
                self.add_form(default_var)
                variable = self.get_one_by_name(default_var['name'])
            elif variable.description != default_var['description']:
                self._db.update_by_id(variable.id, {"description": default_var['description']})

            if variable.name == 'last_restart':
                self._db.update_by_id(variable.id, {"value": time.time()})

    def get_variable_map(self) -> Dict[str, Variable]:
        var_map = {}

        for var in self.get_all():
            var_map[var.name] = var

        return var_map

    @staticmethod
    def hydrate_object(raw_variable: dict, id: Optional[str] = None) -> Variable:
        if id:
            raw_variable['id'] = id

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

    def get_one_by_name(self, name: str) -> Optional[Variable]:
        return self.get_one_by(query=lambda v: v['name'] == name)

    def get_one_by(self, query) -> Optional[Variable]:
        variables = self.hydrate_dict(self._db.get_by_query(query=query))
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

    def get_editable_variables(self) -> List[Variable]:
        return [variable for variable in self.get_all() if variable.editable]

    def get_readonly_variables(self) -> List[Variable]:
        return [variable for variable in self.get_all() if not variable.editable]

    def update_form(self, id: str, value: Union[int, bool, str]) -> None:
        self._db.update_by_id(id, {"value": value})

    def update_by_name(self, name: str, value) -> Optional[Variable]:
        return self._db.update_by_query(query=lambda v: v['name'] == name, new_data={"value": value})

    def add_form(self, variable: Union[Variable, Dict]) -> None:
        db_variable = variable

        if not isinstance(variable, dict):
            db_variable = variable.to_dict()
            del db_variable['id']

        self._db.add(db_variable)

    def delete(self, id: str) -> None:
        self._db.delete_by_id(id)

    def to_dict(self, variables: List[Variable]) -> dict:
        return [variable.to_dict() for variable in variables]

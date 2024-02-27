from typing import Dict, Optional, List, Tuple, Union
from src.model.Variable import Variable
from pysondb import PysonDB
from pysondb.errors import IdDoesNotExistError


class VariableManager:

    DB_FILE = "data/db/settings.json"

    def __init__(self):
        self._db = PysonDB(self.DB_FILE)
        self.init()

    def init(self, lang_dict: Optional[Dict] = None) -> None:
        default_vars = [
            {"name": "port", "value": 5000, "description": lang_dict['settings_variable_help_port'] if lang_dict else ""},
            {"name": "bind", "value": '0.0.0.0', "description": lang_dict['settings_variable_help_bind'] if lang_dict else ""},
            {"name": "lang", "value": "en", "description": lang_dict['settings_variable_help_lang'] if lang_dict else ""},
            {"name": "fleet_enabled", "value": "0", "description": lang_dict['settings_variable_help_fleet_enabled'] if lang_dict else ""},
        ]

        for default_var in default_vars:
            variable = self.get_one_by(query=lambda v: v['name'] == default_var['name'])

            if not variable:
                self.add_form(default_var)
            elif variable.description != default_var['description']:
                self._db.update_by_id(variable.id, {"description": default_var['description']})

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
            self.hydrate_object(self._db.get_by_id(id), id)
        except IdDoesNotExistError:
            return None

    def get_by(self, query) -> List[Variable]:
        return self.hydrate_dict(self._db.get_by_query(query=query))

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

    def update_form(self, id: str, value: Union[int, bool, str]) -> None:
        self._db.update_by_id(id, {"value": value})

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

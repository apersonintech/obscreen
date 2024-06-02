from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.NodeStudio import NodeStudio
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager


class NodeStudioManager(ModelManager):

    TABLE_NAME = "fleet_studio"
    TABLE_MODEL = [
        "name CHAR(255)",
        "enabled INTEGER DEFAULT 0",
        "position INTEGER",
        "host CHAR(255)",
        "port INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_node_studio: dict, id: Optional[int] = None) -> NodeStudio:
        if id:
            raw_node_studio['id'] = id

        return NodeStudio(**raw_node_studio)

    def hydrate_list(self, raw_node_studios: list) -> List[NodeStudio]:
        return [self.hydrate_object(raw_node_studio) for raw_node_studio in raw_node_studios]

    def get(self, id: int) -> Optional[NodeStudio]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[NodeStudio]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[NodeStudio]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: bool = False) -> List[NodeStudio]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, "position" if sort else None))

    def get_enabled_node_studios(self) -> List[NodeStudio]:
        return self.get_by(query="enabled = 1", sort="position")

    def get_disabled_node_studios(self) -> List[NodeStudio]:
        return self.get_by(query="enabled = 0", sort="position")

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"enabled": enabled, "position": 999})
        
    def update_positions(self, positions: list) -> None:
        for node_studio_id, node_studio_position in positions.items():
            self._db.update_by_id(self.TABLE_NAME, node_studio_id, {"position": node_studio_position})

    def update_form(self, id: int, name: str, host: str, port: int) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"name": name, "host": host, "port": port})

    def add_form(self, node_studio: Union[NodeStudio, Dict]) -> None:
        form = node_studio

        if not isinstance(node_studio, dict):
            form = node_studio.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, form)

    def delete(self, id: int) -> None:
        self._db.delete_by_id(self.TABLE_NAME, id)

    def to_dict(self, node_studios: List[NodeStudio]) -> List[Dict]:
        return [node_studio.to_dict() for node_studio in node_studios]

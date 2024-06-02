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
        "port INTEGER",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
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

    def forget_user(self, user_id: int):
        node_studios = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_node_studios = self.user_manager.forget_user_for_entity(node_studios, user_id)

        for node_studio_id, edits in edits_node_studios.items():
            self._db.update_by_id(self.TABLE_NAME, node_studio_id, edits)

    def pre_add(self, node_studio: Dict) -> Dict:
        self.user_manager.track_user_on_create(node_studio)
        self.user_manager.track_user_on_update(node_studio)
        return node_studio

    def pre_update(self, node_studio: Dict) -> Dict:
        self.user_manager.track_user_on_update(node_studio)
        return node_studio

    def pre_delete(self, node_studio_id: str) -> str:
        return node_studio_id

    def post_add(self, node_studio_id: str) -> str:
        return node_studio_id

    def post_update(self, node_studio_id: str) -> str:
        return node_studio_id

    def post_delete(self, node_studio_id: str) -> str:
        return node_studio_id

    def get_enabled_node_studios(self) -> List[NodeStudio]:
        return self.get_by(query="enabled = 1", sort="position")

    def get_disabled_node_studios(self) -> List[NodeStudio]:
        return self.get_by(query="enabled = 0", sort="position")

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update({"enabled": enabled, "position": 999}))
        self.post_update(id)

    def update_positions(self, positions: list) -> None:
        for node_studio_id, node_studio_position in positions.items():
            self._db.update_by_id(self.TABLE_NAME, node_studio_id, {"position": node_studio_position})

    def update_form(self, id: int, name: str, host: str, port: int) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update({"name": name, "host": host, "port": port}))
        self.post_update(id)

    def add_form(self, node_studio: Union[NodeStudio, Dict]) -> None:
        form = node_studio

        if not isinstance(node_studio, dict):
            form = node_studio.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(node_studio.id)

    def delete(self, id: int) -> None:
        self.pre_delete(id)
        self._db.delete_by_id(self.TABLE_NAME, id)
        self.post_delete(id)

    def to_dict(self, node_studios: List[NodeStudio]) -> List[Dict]:
        return [node_studio.to_dict() for node_studio in node_studios]

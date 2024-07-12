from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.NodePlayer import NodePlayer
from src.model.enum.OperatingSystem import OperatingSystem
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager


class NodePlayerManager(ModelManager):

    TABLE_NAME = "fleet_player"
    TABLE_MODEL = [
        "name CHAR(255)",
        "host CHAR(255)",
        "operating_system CHAR(100)",
        "folder_id INTEGER",
        "group_id INTEGER",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_node_player: dict, id: Optional[int] = None) -> NodePlayer:
        if id:
            raw_node_player['id'] = id

        [raw_node_player, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_node_player)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(self.TABLE_NAME, raw_node_player['id'], user_tracker_edits)

        return NodePlayer(**raw_node_player)

    def hydrate_list(self, raw_node_players: list) -> List[NodePlayer]:
        return [self.hydrate_object(raw_node_player) for raw_node_player in raw_node_players]

    def get(self, id: int) -> Optional[NodePlayer]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[NodePlayer]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[NodePlayer]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: Optional[str] = 'created_at', ascending=False) -> List[NodePlayer]:
        return self.hydrate_list(self._db.get_all(table_name=self.TABLE_NAME, sort=sort, ascending=ascending))

    def get_all_indexed(self, attribute: str = 'id', multiple=False) -> Dict[str, NodePlayer]:
        index = {}

        for item in self.get_node_players():
            id = getattr(item, attribute)
            if multiple:
                if id not in index:
                    index[id] = []
                index[id].append(item)
            else:
                index[id] = item

        return index

    def forget_for_user(self, user_id: int):
        node_players = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_node_players = self.user_manager.forget_user_for_entity(node_players, user_id)

        for node_player_id, edits in edits_node_players.items():
            self._db.update_by_id(self.TABLE_NAME, node_player_id, edits)

    def get_node_players(self, group_id: Optional[int] = None, folder_id: Optional[id] = None) -> List[NodePlayer]:
        query = " 1=1 "

        if group_id:
            query = "{} {}".format(query, "AND group_id = {}".format(group_id))

        if folder_id:
            query = "{} {}".format(query, "AND folder_id = {}".format(folder_id))

        return self.get_by(query=query)

    def pre_add(self, node_player: Dict) -> Dict:
        self.user_manager.track_user_on_create(node_player)
        self.user_manager.track_user_on_update(node_player)
        return node_player

    def pre_update(self, node_player: Dict) -> Dict:
        self.user_manager.track_user_on_update(node_player)
        return node_player

    def pre_delete(self, node_player_id: str) -> str:
        return node_player_id

    def post_add(self, node_player_id: str) -> str:
        return node_player_id

    def post_update(self, node_player_id: str) -> str:
        return node_player_id

    def post_delete(self, node_player_id: str) -> str:
        return node_player_id

    def update_form(self, id: int, name: str, host: Optional[str] = None, operating_system: Optional[OperatingSystem] = None, group_id: Optional[int] = None) -> NodePlayer:
        node_player = self.get(id)

        if not node_player:
            return

        form = {
            "name": name,
            "host": host if host else node_player.host,
            "operating_system": operating_system.value if operating_system else node_player.operating_system.value,
            "group_id": group_id if group_id else node_player.group_id
        }

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)
        return self.get(id)

    def add_form(self, node_player: Union[NodePlayer, Dict]) -> None:
        form = node_player

        if not isinstance(node_player, dict):
            form = node_player.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(node_player.id)

    def delete(self, id: int) -> None:
        self.pre_delete(id)
        self._db.delete_by_id(self.TABLE_NAME, id)
        self.post_delete(id)

    def to_dict(self, node_players: List[NodePlayer]) -> List[Dict]:
        return [node_player.to_dict() for node_player in node_players]

    def count_node_players_for_group(self, id: int) -> int:
        return len(self.get_node_players(group_id=id))

    def count_node_players_for_folder(self, folder_id: int) -> int:
        return len(self.get_node_players(folder_id=folder_id))

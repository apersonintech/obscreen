from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.NodePlayerGroup import NodePlayerGroup
from src.util.utils import slugify, slugify_next
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.manager.NodePlayerManager import NodePlayerManager
from src.service.ModelManager import ModelManager


class NodePlayerGroupManager(ModelManager):

    TABLE_NAME = "fleet_player_group"
    TABLE_MODEL = [
        "name CHAR(255)",
        "slug CHAR(255)",
        "playlist_id INTEGER",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_node_player_group: dict, id: Optional[int] = None) -> NodePlayerGroup:
        if id:
            raw_node_player_group['id'] = id

        [raw_node_player_group, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_node_player_group)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(self.TABLE_NAME, raw_node_player_group['id'], user_tracker_edits)

        return NodePlayerGroup(**raw_node_player_group)

    def hydrate_list(self, raw_node_player_groups: list) -> List[NodePlayerGroup]:
        return [self.hydrate_object(raw_node_player_group) for raw_node_player_group in raw_node_player_groups]

    def get(self, id: int) -> Optional[NodePlayerGroup]:
        if not id:
            return None

        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None, values: dict = {}) -> List[NodePlayerGroup]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort, values=values))

    def get_one_by(self, query, values: dict = {}, sort: Optional[str] = None, ascending=True, limit: Optional[int] = None) -> Optional[NodePlayerGroup]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query, values=values, sort=sort, ascending=ascending, limit=limit)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_player_counters_by_player_groups(self, group_id: Optional[int] = None):
        pcounters = self._db.execute_read_query("select group_id, count(distinct id) as total_counter FROM {} GROUP BY group_id".format(
            NodePlayerManager.TABLE_NAME,
            "WHERE 1=1 {}".format(
                " AND group_id = {}".format(group_id) if group_id else ""
            )
        ))
        map = {}
        for pcounter in pcounters:
            map[pcounter['group_id']] = pcounter['total_counter']

        if group_id:
            return map[group_id] if group_id in map else 0

        return map

    def get_all(self, sort: Optional[str] = 'created_at', ascending=False) -> List[NodePlayerGroup]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, sort=sort, ascending=ascending))

    def get_all_labels_indexed(self) -> Dict:
        index = {}

        for item in self.get_all():
            index[item.id] = item.name

        return index

    def get_node_players_groups(self, playlist_id: Optional[int] = None) -> List[NodePlayerGroup]:
        query = " 1=1 "

        if playlist_id:
            query = "{} {}".format(query, "AND playlist_id = {}".format(playlist_id))

        return self.get_by(query=query, sort="name")

    def forget_for_user(self, user_id: int):
        node_player_groups = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_node_player_groups = self.user_manager.forget_user_for_entity(node_player_groups, user_id)

        for node_player_group_id, edits in edits_node_player_groups.items():
            self._db.update_by_id(self.TABLE_NAME, node_player_group_id, edits)

    def get_available_slug(self, slug) -> str:
        known_group = {"slug": slug}
        next_slug = slug
        while known_group is not None:
            next_slug = slugify_next(next_slug)
            known_group = self.get_one_by(query="slug = ?", values={"slug": next_slug}, sort="created_at", ascending=False, limit=1)

        return next_slug

    def slugify(self, node_player_group: Dict) -> Dict:
        node_player_group["slug"] = slugify(node_player_group["name"])

        known_group = self.get_one_by(query="slug = ?", values={
            "slug": node_player_group["slug"]
        }, sort="created_at", ascending=False, limit=1)

        if known_group:
            node_player_group["slug"] = self.get_available_slug(node_player_group["slug"])

        return node_player_group

    def pre_add(self, node_player_group: Dict) -> Dict:
        node_player_group = self.slugify(node_player_group)
        self.user_manager.track_user_on_create(node_player_group)
        self.user_manager.track_user_on_update(node_player_group)
        return node_player_group

    def pre_update(self, node_player_group: Dict) -> Dict:
        node_player_group = self.slugify(node_player_group)
        self.user_manager.track_user_on_update(node_player_group)
        return node_player_group

    def pre_delete(self, node_player_group_id: str) -> str:
        return node_player_group_id

    def post_add(self, node_player_group_id: str) -> str:
        return node_player_group_id

    def post_update(self, node_player_group_id: str) -> str:
        return node_player_group_id

    def post_delete(self, node_player_group_id: str) -> str:
        return node_player_group_id

    def update_form(self, id: int, name: str, playlist_id: Optional[int]) -> None:
        node_player_group = self.get(id)

        if not node_player_group:
            return

        form = {
            "name": name,
            "playlist_id": playlist_id if playlist_id else node_player_group.playlist_id
        }

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)

    def add_form(self, node_player_group: Union[NodePlayerGroup, Dict]) -> NodePlayerGroup:
        form = node_player_group

        if not isinstance(node_player_group, dict):
            form = node_player_group.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        node_player_group = self.get_one_by(query="slug = ?", values={
            "slug": form["slug"]
        })
        self.post_add(node_player_group.id)
        return node_player_group

    def delete(self, id: int) -> None:
        node_player_group = self.get(id)

        if node_player_group:
            self.pre_delete(id)
            self._db.delete_by_id(self.TABLE_NAME, id)
            self.post_delete(id)

    def to_dict(self, node_player_groups: List[NodePlayerGroup]) -> List[Dict]:
        return [node_player_group.to_dict() for node_player_group in node_player_groups]

    def count_node_player_groups_for_playlist(self, id: int) -> int:
        return len(self.get_node_players_groups(playlist_id=id))

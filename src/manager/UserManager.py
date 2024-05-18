import hashlib
import time
from typing import Dict, Optional, List, Tuple, Union
from flask_login import current_user

from src.model.entity.User import User
from src.model.entity.Slide import Slide
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager


class UserManager:

    TABLE_NAME = "user"
    TABLE_MODEL = [
        "username CHAR(255)",
        "password CHAR(255)",
        "enabled INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, on_user_delete):
        self._on_user_delete = on_user_delete
        self._lang_manager = lang_manager
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)
        self._user_map = {}
        self.reload()

    def reload(self) -> None:
        self._user_map = self.prepare_map()

    def map(self) -> dict:
        return self._user_map

    def prepare_map(self) -> Dict[str, User]:
        return self.list_to_map(self.get_all())

    @staticmethod
    def list_to_map(list: List[User]) -> Dict[str, User]:
        user_map = {}

        for user in list:
            user_map[user.id] = user

        return user_map

    def hydrate_object(self, raw_user: dict, id: Optional[int] = None) -> User:
        if id:
            raw_user['id'] = id

        return User(**raw_user)

    def hydrate_list(self, raw_users: list) -> List[User]:
        return [self.hydrate_object(raw_user) for raw_user in raw_users]

    def get(self, id: int) -> Optional[User]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[User]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[User]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_one_by_username(self, username: str, enabled: bool = None) -> Optional[User]:
        return self.get_one_by("username = '{}' and (enabled is null or enabled = {})".format(username, int(enabled)))

    def count_all_enabled(self):
        return len(self.get_enabled_users())

    def track_user_created(self, id_or_entity: Optional[str]) -> User:
        return self.track_user_action(id_or_entity, 'created_by')

    def track_user_updated(self, id_or_entity: Optional[str]) -> User:
        return self.track_user_action(id_or_entity, 'updated_by')

    def track_user_action(self, id_or_entity: Optional[int], attribute: Optional[str] = 'created_by') -> User:
        if not isinstance(id_or_entity, int):
            id_or_entity = getattr(id_or_entity, attribute)

        try:
            id_or_entity = int(id_or_entity)
        except ValueError:
            return User(username=id_or_entity, enabled=False)

        user_map = self.prepare_map()

        if id_or_entity in user_map:
            return user_map[id_or_entity]

        if id_or_entity:
            return User(username=id_or_entity, enabled=False)

        return User(username=self._lang_manager.translate('anonymous'), enabled=False)

    def get_all(self, sort: bool = False) -> List[User]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, "username" if sort else None))

    def get_enabled_users(self) -> List[User]:
        return self.get_by(query="enabled = 1", sort="username")

    def get_disabled_users(self) -> List[User]:
        return self.get_by(query="enabled = 0", sort="username")

    def pre_add(self, user: Dict) -> Dict:
        return user

    def pre_update(self, user: Dict) -> Dict:
        return user

    def pre_delete(self, user_id: int) -> int:
        self._on_user_delete(user_id)
        return user_id

    def post_add(self, user_id: int) -> int:
        self.reload()
        return user_id

    def post_update(self, user_id: int) -> int:
        self.reload()
        return user_id

    def post_delete(self, user_id: int) -> int:
        self.reload()
        return user_id

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update({"enabled": enabled}))
        self.post_update(id)

    def update_form(self, id: int, username: str, password: Optional[str]) -> None:
        form = {"username": username}

        if password is not None and password:
            form['password'] = self.encode_password(password)

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)

    def add_form(self, user: Union[User, Dict]) -> None:
        form = user

        if not isinstance(user, dict):
            form = user.to_dict()
            del form['id']

        form['password'] = self.encode_password(form['password'])

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(user.id)

    def delete(self, id: int) -> None:
        self.pre_delete(id)
        self._db.delete_by_id(self.TABLE_NAME, id)
        self.post_delete(id)

    def to_dict(self, users: List[User]) -> List[Dict]:
        return [user.to_dict() for user in users]

    def encode_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def initialize_user_trackers(self, object: dict) -> dict:
        edits = {}
        user_id = self.get_logged_user("id")
        now = time.time()

        if 'created_by' not in object or not object['created_by']:
            object["created_by"] = user_id
            edits['created_by'] = object['created_by']

        if 'updated_by' not in object or not object['updated_by']:
            object["updated_by"] = user_id
            edits['updated_by'] = object['updated_by']

        if 'created_at' not in object or not object['created_at']:
            object["created_at"] = now
            edits['created_at'] = object['created_at']

        if 'updated_at' not in object or not object['updated_at']:
            object["updated_at"] = now
            edits['updated_at'] = object['updated_at']

        return [object, edits]

    def track_user_on_create(self, object: dict) -> dict:
        object["created_at"] = time.time()
        object["created_by"] = self.get_logged_user("id")
        return object

    def track_user_on_update(self, object: dict) -> dict:
        object["updated_at"] = time.time()
        object["updated_by"] = self.get_logged_user("id")
        return object

    def get_logged_user(self, attribute: Optional[str]) -> Union[User, None, str]:
        if current_user and current_user.is_authenticated:
            if attribute:
                return getattr(current_user, attribute)
            return current_user

        return None

    def forget_user(self, objects: List, user_id: int) -> Dict:
        user_map = self.prepare_map()
        user_id = int(user_id)
        edits = {}

        for object in objects:
            edits[object.id] = {}

            if int(object.created_by) == user_id and user_id in user_map:
                edits[object.id]['created_by'] = user_map[user_id].username

            if int(object.updated_by) == user_id and user_id in user_map:
                edits[object.id]['updated_by'] = user_map[user_id].username

        return edits

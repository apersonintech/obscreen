import hashlib
from pysondb.errors import IdDoesNotExistError
from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.User import User
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.service.ModelManager import ModelManager


class UserManager(ModelManager):

    TABLE_NAME = "user"
    TABLE_MODEL = [
        "username",
        "password",
        "enabled"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager):
        super().__init__(lang_manager, database_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    @staticmethod
    def hydrate_object(raw_user: dict, id: Optional[str] = None) -> User:
        if id:
            raw_user['id'] = id

        return User(**raw_user)

    @staticmethod
    def hydrate_dict(raw_users: dict) -> List[User]:
        return [UserManager.hydrate_object(raw_user, raw_id) for raw_id, raw_user in raw_users.items()]

    @staticmethod
    def hydrate_list(raw_users: list) -> List[User]:
        return [UserManager.hydrate_object(raw_user) for raw_user in raw_users]

    def get(self, id: str) -> Optional[User]:
        try:
            return self.hydrate_object(self._db.get_by_id(id), id)
        except IdDoesNotExistError:
            return None

    def get_by(self, query) -> List[User]:
        return self.hydrate_dict(self._db.get_by_query(query=query))

    def get_one_by(self, query) -> Optional[User]:
        users = self.hydrate_dict(self._db.get_by_query(query=query))
        if len(users) == 1:
            return users[0]
        elif len(users) > 1:
            raise Error("More than one result for query")
        return None

    def get_one_by_username(self, username: str, enabled: bool = None) -> Optional[User]:
        return self.get_one_by(query=lambda v: v['username'] == username and (enabled is None or v['enabled'] == enabled))

    def count_all(self):
        return len(self.get_all())

    def get_all(self, sort: bool = False) -> List[User]:
        raw_users = self._db.get_all()

        if isinstance(raw_users, dict):
            if sort:
                return sorted(UserManager.hydrate_dict(raw_users), key=lambda x: x.username)
            return UserManager.hydrate_dict(raw_users)

        return UserManager.hydrate_list(sorted(raw_users, key=lambda x: x['username']) if sort else raw_users)

    def get_enabled_users(self) -> List[User]:
        return [user for user in self.get_all(sort=True) if user.enabled]

    def get_disabled_users(self) -> List[User]:
        return [user for user in self.get_all(sort=True) if not user.enabled]

    def update_enabled(self, id: str, enabled: bool) -> None:
        self._db.update_by_id(id, {"enabled": enabled})

    def update_form(self, id: str, username: str, password: Optional[str]) -> None:
        form = {"username": username}

        if password is not None and password:
            form['password'] = self.encode_password(password)

        self._db.update_by_id(id, form)

    def add_form(self, user: Union[User, Dict]) -> None:
        form = user

        if not isinstance(user, dict):
            form = user.to_dict()
            del form['id']

        form['password'] = self.encode_password(form['password'])

        self._db.add(form)

    def delete(self, id: str) -> None:
        self._db.delete_by_id(id)

    def to_dict(self, users: List[User]) -> List[Dict]:
        return [user.to_dict() for user in users]

    def encode_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
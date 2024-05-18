import json

from typing import Optional, Union


class User:

    def __init__(self, username: str = '', password: str = '', enabled: bool = True, id: Optional[int] = None):
        self._id = id if id else None
        self._username = username
        self._password = password
        self._enabled = enabled

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        self._username = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value

    @property
    def enabled(self) -> bool:
        return bool(self._enabled)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = bool(value)

    def __str__(self) -> str:
        return f"User(" \
               f"id='{self.id}',\n" \
               f"username='{self.username}',\n" \
               f"enabled='{self.enabled}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "enabled": self.enabled,
        }

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.enabled

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

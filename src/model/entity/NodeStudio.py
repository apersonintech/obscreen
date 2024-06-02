import json
import time

from typing import Optional, Union


class NodeStudio:

    def __init__(self, host: str = '', port: int = 5000, enabled: bool = False, name: str = 'Untitled', position: int = 999, id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._id = id if id else None
        self._host = host
        self._port = port
        self._enabled = enabled
        self._name = name
        self._position = position
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int):
        self._port = value

    @property
    def enabled(self) -> bool:
        return bool(self._enabled)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = bool(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        self._position = value

    @property
    def created_by(self) -> str:
        return self._created_by

    @created_by.setter
    def created_by(self, value: str):
        self._created_by = value

    @property
    def updated_by(self) -> str:
        return self._updated_by

    @updated_by.setter
    def updated_by(self, value: str):
        self._updated_by = value

    @property
    def created_at(self) -> int:
        return self._created_at

    @created_at.setter
    def created_at(self, value: int):
        self._created_at = value

    @property
    def updated_at(self) -> int:
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: int):
        self._updated_at = value

    def __str__(self) -> str:
        return f"NodeStudio(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"enabled='{self.enabled}',\n" \
               f"position='{self.position}',\n" \
               f"host='{self.host}',\n" \
               f"port='{self.port}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict()

        for k, v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "position": self.position,
            "host": self.host,
            "port": self.port,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

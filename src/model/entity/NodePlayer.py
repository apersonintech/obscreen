import json
import time

from typing import Optional, Union
from src.model.enum.OperatingSystem import OperatingSystem
from src.util.utils import str_to_enum


class NodePlayer:

    def __init__(self, host: str = '', name: str = 'Untitled', operating_system: Optional[OperatingSystem] = None, id: Optional[int] = None, group_id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None, folder_id: Optional[int] = None):
        self._id = id if id else None
        self._group_id = group_id
        self._host = host
        self._operating_system = str_to_enum(operating_system, OperatingSystem) if isinstance(operating_system, str) else operating_system
        self._name = name
        self._folder_id = folder_id
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def group_id(self) -> Optional[int]:
        return self._group_id

    @group_id.setter
    def group_id(self, value: Optional[int]):
        self._group_id = value

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

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
    def folder_id(self) -> Optional[int]:
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: Optional[int]):
        self._folder_id = value

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

    @property
    def operating_system(self) -> Optional[OperatingSystem]:
        return self._operating_system

    @operating_system.setter
    def operating_system(self, value: Optional[OperatingSystem]):
        self._operating_system = value

    def __str__(self) -> str:
        return f"NodePlayer(" \
               f"id='{self.id}',\n" \
               f"group_id='{self.group_id}',\n" \
               f"name='{self.name}',\n" \
               f"operating_system='{self.operating_system}',\n" \
               f"host='{self.host}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f"folder_id='{self.folder_id}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict()

        for k, v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "group_id": self.group_id,
            "name": self.name,
            "operating_system": self.operating_system.value,
            "host": self.host,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "folder_id": self.folder_id,
        }

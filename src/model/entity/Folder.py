import json
import time

from typing import Optional, Union

from src.model.enum.FolderEntity import FolderEntity
from src.util.utils import str_to_enum


class Folder:

    def __init__(self, entity: Union[FolderEntity, str] = FolderEntity.NODE_PLAYER, name: str = 'Untitled', parent_id: Optional[int] = None, id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None, depth: Optional[int] = None):
        self._id = id if id else None
        self._parent_id = parent_id
        self._entity = str_to_enum(entity, FolderEntity) if isinstance(entity, str) else entity
        self._name = name
        self._depth = depth
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())
        self._previous = None

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def parent_id(self) -> Optional[int]:
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value: Optional[int]):
        self._parent_id = value

    def set_previous(self, value):
        self._previous = value

    def get_previous(self):
        self._previous

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def entity(self) -> FolderEntity:
        return self._entity

    @entity.setter
    def entity(self, value: FolderEntity):
        self._entity = value

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

    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, value: int):
        self._depth = value

    def __str__(self) -> str:
        return f"NodePlayer(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"parent_id='{self.parent_id}',\n" \
               f"entity='{self.entity}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f"depth='{self.depth}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "entity": self.entity.value,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "depth": self.depth,
        }

    def is_root(self) -> bool:
        return not self._parent_id
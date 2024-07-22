import json
import time
import uuid
import math

from typing import Optional, Union

from src.model.enum.FolderEntity import FolderEntity
from src.util.utils import str_to_enum


class ExternalStorage:

    def __init__(self, uuid: str = '', total_size: int = 0, logical_name: str = '', mount_point: str = '', content_id: Optional[int] = None, id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._uuid = uuid if uuid else self.generate_and_set_uuid()
        self._id = id if id else None
        self._total_size = total_size
        self._logical_name = logical_name
        self._mount_point = mount_point
        self._content_id = content_id
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    def generate_and_set_uuid(self) -> str:
        self._uuid = str(uuid.uuid4())

        return self._uuid

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value
        
    @property
    def content_id(self) -> Optional[int]:
        return self._content_id

    @content_id.setter
    def content_id(self, value: Optional[int]):
        self._content_id = value

    @property
    def total_size(self) -> int:
        return self._total_size

    @total_size.setter
    def total_size(self, value: int):
        self._total_size = value

    @property
    def logical_name(self) -> str:
        return self._logical_name

    @logical_name.setter
    def logical_name(self, value: str):
        self._logical_name = value

    @property
    def mount_point(self) -> str:
        return self._mount_point

    @mount_point.setter
    def mount_point(self, value: str):
        self._mount_point = value

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
        return f"ExternalStorage(" \
               f"id='{self.id}',\n" \
               f"uuid='{self.uuid}',\n" \
               f"total_size='{self.total_size}',\n" \
               f"logical_name='{self.logical_name}',\n" \
               f"mount_point='{self.mount_point}',\n" \
               f"content_id='{self.content_id}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "total_size": self.total_size,
            "logical_name": self.logical_name,
            "mount_point": self.mount_point,
            "content_id": self.content_id,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def total_size_in_gigabytes(self) -> str:
        return f"{self.total_size / (1024 ** 3):.2f}"



import json
import time
import uuid

from typing import Optional, Union
from src.model.enum.ContentType import ContentType, ContentInputType
from src.util.utils import str_to_enum


class Content:

    def __init__(self, uuid: str = '', location: str = '', type: Union[ContentType, str] = ContentType.URL, name: str = 'Untitled', id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None, folder_id: Optional[int] = None):
        self._uuid = uuid if uuid else self.generate_and_set_uuid()
        self._id = id if id else None
        self._location = location
        self._type = str_to_enum(type, ContentType) if isinstance(type, str) else type
        self._name = name
        self._folder_id = folder_id
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
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str):
        self._location = value

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
    def folder_id(self) -> Optional[int]:
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: Optional[int]):
        self._folder_id = value

    @property
    def type(self) -> ContentType:
        return self._type

    @type.setter
    def type(self, value: ContentType):
        self._type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def __str__(self) -> str:
        return f"Content(" \
               f"id='{self.id}',\n" \
               f"uuid='{self.uuid}',\n" \
               f"name='{self.name}',\n" \
               f"type='{self.type}',\n" \
               f"location='{self.location}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f"folder_id='{self.folder_id}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict(with_virtual=True)

        for k, v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self, with_virtual: bool = False) -> dict:
        content = {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type.value,
            "location": self.location,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "folder_id": self.folder_id,
        }

        if with_virtual:
            content['is_editable'] = self.is_editable()

        return content

    def has_file(self) -> bool:
        return (
            self.type == ContentType.VIDEO
            or self.type == ContentType.PICTURE
        )

    def get_input_type(self) -> ContentInputType:
        return ContentType.get_input(self.type)

    def is_editable(self) -> bool:
        return ContentInputType.is_editable(self.get_input_type())

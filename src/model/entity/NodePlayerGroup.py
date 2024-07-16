import json
import time

from typing import Optional, Union


class NodePlayerGroup:

    def __init__(self, name: str = 'Untitled', slug: str = 'untitled', playlist_id: Optional[int] = None, id: Optional[int] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._id = id if id else None
        self._playlist_id = playlist_id
        self._name = name
        self._slug = slug
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def playlist_id(self) -> Optional[int]:
        return self._playlist_id

    @playlist_id.setter
    def playlist_id(self, value: Optional[int]):
        self._playlist_id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def slug(self) -> str:
        return self._slug

    @slug.setter
    def slug(self, value: str):
        self._slug = value

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
        return f"NodePlayer(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"slug='{self.slug}',\n" \
               f"playlist_id='{self.playlist_id}',\n" \
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
            "slug": self.slug,
            "playlist_id": self.playlist_id,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def is_root(self) -> bool:
        return not self._playlist_id
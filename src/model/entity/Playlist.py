import json
import time

from typing import Optional, Union


class Playlist:

    def __init__(self, name: str = 'Untitled', slug: str = 'untitled', id: Optional[int] = None, enabled: bool = False, time_sync: bool = True, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._id = id if id else None
        self._name = name
        self._slug = slug
        self._enabled = enabled
        self._time_sync = time_sync
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def enabled(self) -> bool:
        return bool(self._enabled)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = bool(value)

    @property
    def time_sync(self) -> bool:
        return bool(self._time_sync)

    @time_sync.setter
    def time_sync(self, value: bool):
        self._time_sync = bool(value)

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

    def __str__(self) -> str:
        return f"Playlist(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"nameslug='{self.slug}',\n" \
               f"enabled='{self.enabled}',\n" \
               f"time_sync='{self.time_sync}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict()

        for k,v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self) -> dict:
        playlist = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "enabled": self.enabled,
            "time_sync": self.time_sync,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        return playlist

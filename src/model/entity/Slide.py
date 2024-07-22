import json
import time

from typing import Optional, Union
from src.util.utils import str_to_enum


class Slide:

    def __init__(self, playlist_id: Optional[int] = None, content_id: Optional[int] = None, delegate_duration=False, duration: int = 3, is_notification: bool = False, enabled: bool = False, position: int = 999, id: Optional[int] = None, cron_schedule: Optional[str] = None, cron_schedule_end: Optional[str] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._id = id if id else None
        self._playlist_id = playlist_id
        self._content_id = content_id
        self._duration = duration
        self._delegate_duration = delegate_duration
        self._enabled = enabled
        self._is_notification = is_notification
        self._position = position
        self._cron_schedule = cron_schedule
        self._cron_schedule_end = cron_schedule_end
        self._created_by = created_by if created_by else None
        self._updated_by = updated_by if updated_by else None
        self._created_at = int(created_at if created_at else time.time())
        self._updated_at = int(updated_at if updated_at else time.time())

    @property
    def id(self) -> Optional[int]:
        return self._id

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
    def playlist_id(self) -> Optional[int]:
        return self._playlist_id

    @playlist_id.setter
    def playlist_id(self, value: Optional[int]):
        self._playlist_id = value

    @property
    def content_id(self) -> Optional[int]:
        return self._content_id

    @content_id.setter
    def content_id(self, value: Optional[int]):
        self._content_id = value

    @property
    def cron_schedule(self) -> Optional[str]:
        return self._cron_schedule

    @cron_schedule.setter
    def cron_schedule(self, value: Optional[str]):
        self._cron_schedule = value

    @property
    def cron_schedule_end(self) -> Optional[str]:
        return self._cron_schedule_end

    @cron_schedule_end.setter
    def cron_schedule_end(self, value: Optional[str]):
        self._cron_schedule_end = value

    @property
    def delegate_duration(self) -> bool:
        return self._delegate_duration

    @delegate_duration.setter
    def delegate_duration(self, value: bool):
        self._delegate_duration = value

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value: int):
        self._duration = value

    @property
    def enabled(self) -> bool:
        return bool(self._enabled)

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = bool(value)

    @property
    def is_notification(self) -> bool:
        return bool(self._is_notification)

    @is_notification.setter
    def is_notification(self, value: bool):
        self._is_notification = bool(value)

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        self._position = value

    def __str__(self) -> str:
        return f"Slide(" \
               f"id='{self.id}',\n" \
               f"enabled='{self.enabled}',\n" \
               f"is_notification='{self.is_notification}',\n" \
               f"duration='{self.duration}',\n" \
               f"delegate_duration='{self.delegate_duration}',\n" \
               f"position='{self.position}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f"playlist_id='{self.playlist_id}',\n" \
               f"content_id='{self.content_id}',\n" \
               f"cron_schedule='{self.cron_schedule}',\n" \
               f"cron_schedule_end='{self.cron_schedule_end}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict()

        for k, v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self) -> dict:
        slide = {
            "id": self.id,
            "enabled": self.enabled,
            "is_notification": self.is_notification,
            "position": self.position,
            "duration": self.duration,
            "delegate_duration": self.delegate_duration,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "playlist_id": self.playlist_id,
            "content_id": self.content_id,
            "cron_schedule": self.cron_schedule,
            "cron_schedule_end": self.cron_schedule_end,
        }

        return slide

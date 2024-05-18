import json
import time

from typing import Optional, Union
from src.model.enum.SlideType import SlideType, SlideInputType
from src.utils import str_to_enum


class Slide:

    def __init__(self, location: str = '', duration: int = 3, type: Union[SlideType, str] = SlideType.URL, enabled: bool = False, name: str = 'Untitled', position: int = 999, id: Optional[int] = None, cron_schedule: Optional[str] = None, cron_schedule_end: Optional[str] = None, created_by: Optional[str] = None, updated_by: Optional[str] = None, created_at: Optional[int] = None, updated_at: Optional[int] = None):
        self._id = id if id else None
        self._location = location
        self._duration = duration
        self._type = str_to_enum(type, SlideType) if isinstance(type, str) else type
        self._enabled = enabled
        self._name = name
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
    def type(self) -> SlideType:
        return self._type

    @type.setter
    def type(self, value: SlideType):
        self._type = value

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

    def __str__(self) -> str:
        return f"Slide(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"type='{self.type}',\n" \
               f"enabled='{self.enabled}',\n" \
               f"duration='{self.duration}',\n" \
               f"position='{self.position}',\n" \
               f"location='{self.location}',\n" \
               f"created_by='{self.created_by}',\n" \
               f"updated_by='{self.updated_by}',\n" \
               f"created_at='{self.created_at}',\n" \
               f"updated_at='{self.updated_at}',\n" \
               f"cron_schedule='{self.cron_schedule}',\n" \
               f"cron_schedule_end='{self.cron_schedule_end}',\n" \
               f")"

    def to_json(self, edits: dict = {}) -> str:
        obj = self.to_dict(with_virtual=True)

        for k,v in edits.items():
            obj[k] = v

        return json.dumps(obj)

    def to_dict(self, with_virtual: bool = False) -> dict:
        slide = {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "position": self.position,
            "type": self.type.value,
            "duration": self.duration,
            "location": self.location,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "cron_schedule": self.cron_schedule,
            "cron_schedule_end": self.cron_schedule_end,
        }

        if with_virtual:
            slide['is_editable'] = self.is_editable()

        return slide

    def has_file(self) -> bool:
        return (
            self.type == SlideType.VIDEO
            or self.type == SlideType.PICTURE
        )

    def get_input_type(self) -> SlideInputType:
        return SlideType.get_input(self.type)

    def is_editable(self) -> bool:
        return SlideInputType.is_editable(self.get_input_type())

import uuid
import json

from typing import Optional
from src.model import SlideType


class Slide:

    def __init__(self, location: str, duration: int, type: SlideType, enabled: bool, name: str, position: int = 999, id: Optional[int] = None):
        self._id = uuid.uuid4().int if id is None else id
        self._location = location
        self._duration = duration
        self._type = type
        self._enabled = enabled
        self._name = name
        self._position = position

    @property
    def id(self) -> int:
        return self._id

    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str):
        self._location = value

    @property
    def type(self) -> SlideType:
        return self._type

    @type.setter
    def type(self, value: SlideType):
        self._type = value

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value: int):
        self._duration = value

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

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
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "enabled": self.enabled,
            "position": self.position,
            "type": self.type,
            "duration": self.duration,
            "location": self.location,
        }

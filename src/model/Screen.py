import json

from typing import Optional, Union


class Screen:

    def __init__(self, address: str = '', enabled: bool = False, name: str = 'Untitled', position: int = 999, id: Optional[str] = None):
        self._id = id if id else None
        self._address = address
        self._enabled = enabled
        self._name = name
        self._position = position

    @property
    def id(self) -> Union[int, str]:
        return self._id

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

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
               f"enabled='{self.enabled}',\n" \
               f"position='{self.position}',\n" \
               f"address='{self.address}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "enabled": self.enabled,
            "position": self.position,
            "address": self.address,
        }

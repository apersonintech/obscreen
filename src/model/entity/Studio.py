import json

from typing import Optional, Union


class Studio:

    def __init__(self, host: str = '', port: int = 5000, enabled: bool = False, name: str = 'Untitled', position: int = 999, id: Optional[int] = None):
        self._id = id if id else None
        self._host = host
        self._port = port
        self._enabled = enabled
        self._name = name
        self._position = position

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int):
        self._port = value

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
        return f"Studio(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"enabled='{self.enabled}',\n" \
               f"position='{self.position}',\n" \
               f"host='{self.host}',\n" \
               f"port='{self.port}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "position": self.position,
            "host": self.host,
            "port": self.port,
        }

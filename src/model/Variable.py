import json

from typing import Optional, Union


class Variable:

    def __init__(self, name: str = '', description: str = '', value: Union[int, bool, str] = '', id: Optional[str] = None):
        self._id = id if id else None
        self._name = name
        self._description = description
        self._value = value

    @property
    def id(self) -> Union[int, str]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def value(self) -> Union[int, bool, str]:
        return self._value

    @value.setter
    def value(self, value: Union[int, bool, str]):
        self._value = value

    def __str__(self) -> str:
        return f"Variable(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"value='{self.value}',\n" \
               f"description='{self.description}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "description": self.description,
        }

    def as_bool(self):
        return bool(int(self._value))

    def as_string(self):
        return str(self._value)

    def as_int(self):
        return int(self._value)
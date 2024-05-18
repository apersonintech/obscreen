import json
import time

from typing import Optional, Union, Dict, List
from src.model.enum.VariableType import VariableType
from src.model.enum.VariableUnit import VariableUnit
from src.model.entity.Selectable import Selectable
from src.utils import str_to_enum


class Variable:

    def __init__(self, name: str = '', section: str = '', description: str = '', description_edition: str = '', type: Union[VariableType, str] = VariableType.STRING,
                 value: Union[int, bool, str] = '', editable: bool = True, id: Optional[int] = None,
                 plugin: Optional[str] = None, selectables: Optional[List[Selectable]] = None, unit: Optional[VariableUnit] = None,
                 refresh_player: bool = False):
        self._id = id if id else None
        self._name = name
        self._section = section
        self._type = str_to_enum(type, VariableType) if isinstance(type, str) else type
        self._description = description
        self._description_edition = description_edition
        self._value = value
        self._editable = editable
        self._plugin = plugin
        self._refresh_player = refresh_player
        self._selectables = selectables

        try:
            self._unit = str_to_enum(unit, VariableUnit) if isinstance(unit, str) else unit
        except ValueError:
            self._unit = None

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def selectables(self) -> List[Selectable]:
        return self._selectables

    @selectables.setter
    def selectables(self, value: List[Selectable]):
        self._selectables = value

    def add_selectable(self, value: Selectable):
        self._selectables.append(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def section(self) -> str:
        return self._section

    @section.setter
    def section(self, value: str):
        self._section = value

    @property
    def type(self) -> VariableType:
        return self._type

    @type.setter
    def type(self, value: VariableType):
        self._type = value

    @property
    def unit(self) -> Optional[VariableUnit]:
        return self._unit

    @unit.setter
    def unit(self, value: Optional[VariableUnit]):
        self._unit = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def description_edition(self) -> str:
        return self._description_edition

    @description_edition.setter
    def description_edition(self, value: str):
        self._description_edition = value

    @property
    def editable(self) -> bool:
        return bool(self._editable)

    @editable.setter
    def editable(self, value: bool):
        self._editable = bool(value)

    @property
    def refresh_player(self) -> bool:
        return bool(self._refresh_player)

    @refresh_player.setter
    def refresh_player(self, value: bool):
        self._refresh_player = bool(value)

    @property
    def value(self) -> Union[int, bool, str]:
        return self._value

    @value.setter
    def value(self, value: Union[int, bool, str]):
        self._value = value

    @property
    def plugin(self) -> Optional[str]:
        return self._plugin

    @plugin.setter
    def plugin(self, value: Optional[str]):
        self._plugin = value

    def __str__(self) -> str:
        return f"Variable(" \
               f"id='{self.id}',\n" \
               f"name='{self.name}',\n" \
               f"section='{self.section}',\n" \
               f"value='{self.value}',\n" \
               f"type='{self.type}',\n" \
               f"unit='{self.unit}',\n" \
               f"description='{self.description}',\n" \
               f"description_edition='{self.description_edition}',\n" \
               f"editable='{self.editable}',\n" \
               f"refresh_player='{self.refresh_player}',\n" \
               f"plugin='{self.plugin}',\n" \
               f"selectables='{self.selectables}',\n" \
               f")"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "section": self.section,
            "value": self.value,
            "type": self.type.value,
            "unit": self.unit.value if self.unit else None,
            "description": self.description,
            "description_edition": self.description_edition,
            "editable": self.editable,
            "refresh_player": self.refresh_player,
            "plugin": self.plugin,
            "selectables": [selectable.to_dict() for selectable in self.selectables] if isinstance(self._selectables, list) else None
        }

    def as_bool(self) -> bool:
        return bool(int(self._value))

    def as_string(self) -> str:
        if self._value is None:
            return ''

        return str(self._value)

    def as_int(self) -> int:
        return int(float(self._value))

    def as_ctime(self) -> int:
        return time.ctime(int(float(self._value)))

    def display(self) -> Union[int, bool, str]:
        value = self.eval()

        if self.type == VariableType.SELECT_SINGLE:
            if isinstance(self._selectables, list):
                for selectable in self.selectables:
                    if selectable.key == value:
                        value = str(selectable.label)
                        break

        if self.unit == VariableUnit.MEGABYTE:
            value = "{} {}".format(
                value,
                "MB"
            )
        elif self.unit == VariableUnit.SECOND:
            value = "{}{}".format(value, "s")

        return value

    def eval(self) -> Union[int, bool, str]:
        if self.type == VariableType.INT:
            return self.as_int()
        elif self.type == VariableType.BOOL:
            return self.as_bool()
        elif self.type == VariableType.TIMESTAMP:
            return self.as_ctime()

        return self.as_string()

    def is_from_plugin(self) -> Optional[str]:
        return self.plugin

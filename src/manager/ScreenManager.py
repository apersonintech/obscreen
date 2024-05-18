from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Screen import Screen
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.service.ModelManager import ModelManager


class ScreenManager(ModelManager):

    TABLE_NAME = "fleet"
    TABLE_MODEL = [
        "name CHAR(255)",
        "enabled INTEGER",
        "position INTEGER",
        "host CHAR(255)",
        "port INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager):
        super().__init__(lang_manager, database_manager, user_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_screen: dict, id: Optional[int] = None) -> Screen:
        if id:
            raw_screen['id'] = id

        return Screen(**raw_screen)

    def hydrate_list(self, raw_screens: list) -> List[Screen]:
        return [self.hydrate_object(raw_screen) for raw_screen in raw_screens]

    def get(self, id: int) -> Optional[Screen]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[Screen]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[Screen]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: bool = False) -> List[Screen]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, "position" if sort else None))

    def get_enabled_screens(self) -> List[Screen]:
        return self.get_by(query="enabled = 1", sort="position")

    def get_disabled_screens(self) -> List[Screen]:
        return self.get_by(query="enabled = 0", sort="position")

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"enabled": enabled, "position": 999})
        
    def update_positions(self, positions: list) -> None:
        for screen_id, screen_position in positions.items():
            self._db.update_by_id(self.TABLE_NAME, screen_id, {"position": screen_position})

    def update_form(self, id: int, name: str, host: str, port: int) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, {"name": name, "host": host, "port": port})

    def add_form(self, screen: Union[Screen, Dict]) -> None:
        form = screen

        if not isinstance(screen, dict):
            form = screen.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, form)

    def delete(self, id: int) -> None:
        self._db.delete_by_id(self.TABLE_NAME, id)

    def to_dict(self, screens: List[Screen]) -> List[Dict]:
        return [screen.to_dict() for screen in screens]

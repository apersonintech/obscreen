import os

from typing import Dict, Optional, List, Tuple, Union
from pysondb.errors import IdDoesNotExistError

from src.model.entity.Slide import Slide
from src.utils import str_to_enum, get_optional_string
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.service.ModelManager import ModelManager


class SlideManager(ModelManager):

    TABLE_NAME = "slideshow"
    TABLE_MODEL = [
        "name",
        "type",
        "enabled",
        "duration",
        "position",
        "location",
        "cron_schedule"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager):
        super().__init__(lang_manager, database_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    @staticmethod
    def hydrate_object(raw_slide: dict, id: str = None) -> Slide:
        if id:
            raw_slide['id'] = id

        return Slide(**raw_slide)

    @staticmethod
    def hydrate_dict(raw_slides: dict) -> List[Slide]:
        return [SlideManager.hydrate_object(raw_slide, raw_id) for raw_id, raw_slide in raw_slides.items()]

    @staticmethod
    def hydrate_list(raw_slides: list) -> List[Slide]:
        return [SlideManager.hydrate_object(raw_slide) for raw_slide in raw_slides]

    def get(self, id: str) -> Optional[Slide]:
        try:
            return self.hydrate_object(self._db.get_by_id(id), id)
        except IdDoesNotExistError:
            return None

    def get_by(self, query) -> List[Slide]:
        return self.hydrate_dict(self._db.get_by_query(query=query))

    def get_one_by(self, query) -> Optional[Slide]:
        slides = self.hydrate_dict(self._db.get_by_query(query=query))
        if len(slides) == 1:
            return slides[0]
        elif len(slides) > 1:
            raise Error("More than one result for query")
        return None

    def get_all(self, sort: bool = False) -> List[Slide]:
        raw_slides = self._db.get_all()

        if isinstance(raw_slides, dict):
            if sort:
                return sorted(SlideManager.hydrate_dict(raw_slides), key=lambda x: x.position)
            return SlideManager.hydrate_dict(raw_slides)

        return SlideManager.hydrate_list(sorted(raw_slides, key=lambda x: x['position']) if sort else raw_slides)

    def get_enabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if slide.enabled]

    def get_disabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if not slide.enabled]

    def update_enabled(self, id: str, enabled: bool) -> None:
        self._db.update_by_id(id, {"enabled": enabled, "position": 999})
        
    def update_positions(self, positions: list) -> None:
        for slide_id, slide_position in positions.items():
            self._db.update_by_id(slide_id, {"position": slide_position})

    def update_form(self, id: str, name: str, duration: int, cron_schedule: Optional[str] = '') -> None:
        self._db.update_by_id(id, {
            "name": name,
            "duration": duration,
            "cron_schedule": get_optional_string(cron_schedule)
        })

    def add_form(self, slide: Union[Slide, Dict]) -> None:
        db_slide = slide

        if not isinstance(slide, dict):
            db_slide = slide.to_dict()
            del db_slide['id']

        self._db.add(db_slide)

    def delete(self, id: str) -> None:
        slide = self.get(id)

        if slide:
            if slide.has_file():
                try:
                    os.unlink(slide.location)
                except FileNotFoundError:
                    pass

            self._db.delete_by_id(id)

    def to_dict(self, slides: List[Slide]) -> dict:
        return [slide.to_dict() for slide in slides]

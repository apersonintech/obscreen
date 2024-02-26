import json

from typing import Dict, Optional, List, Tuple
from src.model.Slide import Slide
from pysondb import db

class SlideManager():

    DB_FILE = "data/slideshow.json"

    def __init__(self):
        self._db = db.getDb(self.DB_FILE)

    @staticmethod
    def hydrate_object(raw_slide) -> Slide:
        return Slide(**raw_slide)

    @staticmethod
    def hydrate_list(raw_slides) -> List[Slide]:
        return [SlideManager.hydrate_object(raw_slide) for raw_slide in raw_slides]

    def get_all(self, sort: bool = False) -> List[Slide]:
        raw_slides = self._db.getAll()
        return SlideManager.hydrate_list(sorted(raw_slides, key=lambda x: x['position']) if sort else raw_slides)

    def get_enabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if slide.enabled]

    def get_disabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if not slide.enabled]

    def update_enabled(self, id: int, enabled: bool) -> None:
        self._db.updateById(id, {"enabled": enabled, "position": 999})
        
    def update_positions(self, positions: list) -> None:
        for slide_id, slide_position in positions.items():
            self._db.updateById(slide_id, {"position": slide_position})

    def update_form(self, id: str, name: str, duration: int) -> None:
        self._db.updateById(id, {"name": name, "duration": duration})

    def reindent(self) -> None:
        with open(self.DB_FILE, 'r') as file:
            data = json.load(file)

        with open(self.DB_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete(self, id: int) -> None:
        self._db.deleteById(id)
        self.reindent()

    def to_dict(self, slides: List[Slide]) -> dict:
        return [slide.to_dict() for slide in slides]

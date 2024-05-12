import os

from typing import Dict, Optional, List, Tuple, Union
from pysondb.errors import IdDoesNotExistError

from src.model.entity.Slide import Slide
from src.model.enum.SlideType import SlideType
from src.utils import get_optional_string, get_yt_video_id
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
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
        "cron_schedule",
        "cron_schedule_end",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager):
        super().__init__(lang_manager, database_manager, user_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_slide: dict, id: str = None) -> Slide:
        if id:
            raw_slide['id'] = id

        [raw_slide, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_slide)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(raw_slide['id'], user_tracker_edits)

        return Slide(**raw_slide)

    def hydrate_dict(self, raw_slides: dict) -> List[Slide]:
        return [self.hydrate_object(raw_slide, raw_id) for raw_id, raw_slide in raw_slides.items()]

    def hydrate_list(self, raw_slides: list) -> List[Slide]:
        return [self.hydrate_object(raw_slide) for raw_slide in raw_slides]

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
                return sorted(self.hydrate_dict(raw_slides), key=lambda x: x.position)
            return self.hydrate_dict(raw_slides)

        return self.hydrate_list(sorted(raw_slides, key=lambda x: x['position']) if sort else raw_slides)

    def get_enabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if slide.enabled]

    def get_disabled_slides(self) -> List[Slide]:
        return [slide for slide in self.get_all(sort=True) if not slide.enabled]

    def pre_add(self, slide: Dict) -> Dict:
        self.user_manager.track_user_on_create(slide)
        self.user_manager.track_user_on_update(slide)
        return slide

    def pre_update(self, slide: Dict) -> Dict:
        self.user_manager.track_user_on_update(slide)
        return slide

    def pre_delete(self, slide_id: str) -> str:
        return slide_id

    def post_add(self, slide_id: str) -> str:
        return slide_id

    def post_update(self, slide_id: str) -> str:
        return slide_id

    def post_updates(self):
        pass

    def post_delete(self, slide_id: str) -> str:
        return slide_id

    def update_enabled(self, id: str, enabled: bool) -> None:
        self._db.update_by_id(id, self.pre_update({"enabled": enabled, "position": 999}))
        self.post_update(id)
        
    def update_positions(self, positions: list) -> None:
        for slide_id, slide_position in positions.items():
            self._db.update_by_id(slide_id, {"position": slide_position})

    def update_form(self, id: str, name: str, duration: int, cron_schedule: Optional[str] = '', cron_schedule_end: Optional[str] = '', location: Optional[str] = None) -> None:
        slide = self.get(id)

        if not slide:
            return

        form = {
            "name": name,
            "duration": duration,
            "cron_schedule": get_optional_string(cron_schedule),
            "cron_schedule_end": get_optional_string(cron_schedule_end)
        }

        if location is not None and location:
            form["location"] = location

        if slide.type == SlideType.YOUTUBE:
            form['location'] = get_yt_video_id(form['location'])

        self._db.update_by_id(id, self.pre_update(form))
        self.post_update(id)

    def add_form(self, slide: Union[Slide, Dict]) -> None:
        form = slide

        if not isinstance(slide, dict):
            form = slide.to_dict()
            del form['id']

        if form['type'] == SlideType.YOUTUBE:
            form['location'] = get_yt_video_id(form['location'])

        self._db.add(self.pre_add(form))
        self.post_add(slide.id)

    def delete(self, id: str) -> None:
        slide = self.get(id)

        if slide:
            if slide.has_file():
                try:
                    os.unlink(slide.location)
                except FileNotFoundError:
                    pass

            self.pre_delete(id)
            self._db.delete_by_id(id)
            self.post_delete(id)

    def to_dict(self, slides: List[Slide]) -> List[Dict]:
        return [slide.to_dict() for slide in slides]


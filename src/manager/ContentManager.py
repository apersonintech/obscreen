import os

from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Content import Content
from src.model.entity.Playlist import Playlist
from src.model.enum.ContentType import ContentType
from src.util.utils import get_yt_video_id
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager
from src.util.UtilFile import randomize_filename


class ContentManager(ModelManager):

    TABLE_NAME = "content"
    TABLE_MODEL = [
        "uuid CHAR(255)",
        "name CHAR(255)",
        "type CHAR(30)",
        "location TEXT",
        "folder_id INTEGER",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_content: dict, id: int = None) -> Content:
        if id:
            raw_content['id'] = id

        [raw_content, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_content)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(self.TABLE_NAME, raw_content['id'], user_tracker_edits)

        return Content(**raw_content)

    def hydrate_list(self, raw_contents: list) -> List[Content]:
        return [self.hydrate_object(raw_content) for raw_content in raw_contents]

    def get(self, id: int) -> Optional[Content]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[Content]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[Content]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: bool = False) -> List[Content]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, sort="created_at" if sort else None, ascending=False))

    def get_all_indexed(self, attribute: str = 'id', multiple=False) -> Dict[str, Content]:
        index = {}

        for item in self.get_contents():
            id = getattr(item, attribute)
            if multiple:
                if id not in index:
                    index[id] = []
                index[id].append(item)
            else:
                index[id] = item

        return index

    def forget_for_user(self, user_id: int):
        contents = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_contents = self.user_manager.forget_user_for_entity(contents, user_id)

        for content_id, edits in edits_contents.items():
            self._db.update_by_id(self.TABLE_NAME, content_id, edits)

    def get_contents(self, slide_id: Optional[id] = None, folder_id: Optional[id] = None) -> List[Content]:
        query = " 1=1 "

        if slide_id:
            query = "{} {}".format(query, "AND slide_id = {}".format(slide_id))

        if folder_id:
            query = "{} {}".format(query, "AND folder_id = {}".format(folder_id))

        return self.get_by(query=query)

    def pre_add(self, content: Dict) -> Dict:
        self.user_manager.track_user_on_create(content)
        self.user_manager.track_user_on_update(content)
        return content

    def pre_update(self, content: Dict) -> Dict:
        self.user_manager.track_user_on_update(content)
        return content

    def pre_delete(self, content_id: str) -> str:
        return content_id

    def post_add(self, content_id: str) -> str:
        return content_id

    def post_update(self, content_id: str) -> str:
        return content_id

    def post_updates(self):
        pass

    def post_delete(self, content_id: str) -> str:
        return content_id

    def update_form(self, id: int, name: str, location: Optional[str] = None) -> Content:
        content = self.get(id)

        if not content:
            return

        form = {
            "name": name,
        }

        if location is not None and location:
            form["location"] = location

        if content.type == ContentType.YOUTUBE:
            form['location'] = get_yt_video_id(form['location'])
        elif content.type == ContentType.URL:
            if not form['location'].startswith('http'):
                form['location'] = "https://{}".format(form['location'])

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)
        return self.get(id)

    def add_form(self, content: Union[Content, Dict]) -> None:
        form = content

        if not isinstance(content, dict):
            form = content.to_dict()
            del form['id']

        if form['type'] == ContentType.YOUTUBE.value:
            form['location'] = get_yt_video_id(form['location'])

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(content.id)

    def add_form_raw(self, name: str, type: ContentType, request_files: Optional[Dict], upload_dir: str, location: Optional[str] = None) -> Content:
        content = Content(
            name=name,
            type=type
        )

        if content.has_file():
            if 'object' not in request_files:
                return redirect(request.url)

            object = request_files['object']

            if object.filename == '':
                return None

            if object:
                object_name = randomize_filename(object.filename)
                object_path = os.path.join(upload_dir, object_name)
                object.save(object_path)
                content.location = object_path
        else:
            content.location = location

        self.add_form(content)
        return self.get_one_by(query="uuid = '{}'".format(content.uuid))

    def delete(self, id: int) -> None:
        content = self.get(id)

        if content:
            if content.has_file():
                try:
                    os.unlink(content.location)
                except FileNotFoundError:
                    pass

            self.pre_delete(id)
            self._db.delete_by_id(self.TABLE_NAME, id)
            self.post_delete(id)

    def to_dict(self, contents: List[Content]) -> List[Dict]:
        return [content.to_dict() for content in contents]

    def count_contents_for_slide(self, slide_id: int) -> int:
        return len(self.get_contents(slide_id=slide_id))

    def count_contents_for_folder(self, folder_id: int) -> int:
        return len(self.get_contents(folder_id=folder_id))

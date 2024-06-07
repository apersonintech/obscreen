from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Folder import Folder
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager


class FolderManager(ModelManager):

    TABLE_NAME = "folder"
    TABLE_MODEL = [
        "name CHAR(255)",
        "parent_id INTEGER",
        "entity CHAR(255)",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_folder: dict, id: Optional[int] = None) -> Folder:
        if id:
            raw_folder['id'] = id

        return Folder(**raw_folder)

    def hydrate_list(self, raw_folders: list) -> List[Folder]:
        return [self.hydrate_object(raw_folder) for raw_folder in raw_folders]

    def get(self, id: int) -> Optional[Folder]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[Folder]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[Folder]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: bool = False) -> List[Folder]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, "name" if sort else None))

    def forget_user(self, user_id: int):
        folders = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_folders = self.user_manager.forget_user_for_entity(folders, user_id)

        for folder_id, edits in edits_folders.items():
            self._db.update_by_id(self.TABLE_NAME, folder_id, edits)

    def pre_add(self, folder: Dict) -> Dict:
        self.user_manager.track_user_on_create(folder)
        self.user_manager.track_user_on_update(folder)
        return folder

    def pre_update(self, folder: Dict) -> Dict:
        self.user_manager.track_user_on_update(folder)
        return folder

    def pre_delete(self, folder_id: str) -> str:
        return folder_id

    def post_add(self, folder_id: str) -> str:
        return folder_id

    def post_update(self, folder_id: str) -> str:
        return folder_id

    def post_delete(self, folder_id: str) -> str:
        return folder_id

    def update_form(self, id: int, name: str) -> None:
        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update({"name": name}))
        self.post_update(id)

    def add_form(self, folder: Union[Folder, Dict]) -> None:
        form = folder

        if not isinstance(folder, dict):
            form = folder.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(folder.id)

    def delete(self, id: int) -> None:
        self.pre_delete(id)
        self._db.delete_by_id(self.TABLE_NAME, id)
        self.post_delete(id)

    def to_dict(self, folders: List[Folder]) -> List[Dict]:
        return [folder.to_dict() for folder in folders]

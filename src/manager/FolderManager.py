from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Folder import Folder
from src.model.enum.FolderEntity import FolderEntity, FOLDER_ROOT_PATH, FOLDER_ROOT_NAME
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
        "depth INTEGER DEFAULT 0",
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

    def get_by_entity(self, entity: FolderEntity) -> List[Folder]:
        return self.get_by("entity = '{}'".format(entity.value))

    def get_children(self, folder: Optional[Folder]) -> List[Folder]:
        if folder:
            return self.get_by("parent_id = {}".format(folder.id))

        return self.get_by("parent_id is null")

    def get_one_by_path(self, path: str, entity: FolderEntity) -> Folder:
        parts = path[1:].split('/')
        return self.get_one_by("name = '{}' and depth = {} and entity = '{}'".format(parts[-1], len(parts) - 1, entity.value))

    def hydrate_parents(self, folder: Optional[Folder]) -> Optional[Folder]:
        if not folder:
            return None

        if not folder.parent_id:
            return folder

        parent = self.get(folder.parent_id)
        folder.set_previous(parent)
        return self.hydrate_parents(parent)

    def get_one_by(self, query) -> Optional[Folder]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: bool = False) -> List[Folder]:
        return self.hydrate_list(self._db.get_all(self.TABLE_NAME, "name" if sort else None))

    def forget_for_user(self, user_id: int):
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

    @staticmethod
    def to_dict(folders: List[Folder]) -> List[Dict]:
        return [folder.to_dict() for folder in folders]

    @staticmethod
    def _build_tree(folders: List[Folder]) -> Dict:
        folder_dict = {}
        for folder in folders:
            if folder.parent_id not in folder_dict:
                folder_dict[folder.parent_id] = []
            folder_dict[folder.parent_id].append(folder)

        def build_nested_dict(parent_id, path):
            children = folder_dict.get(parent_id, [])
            children.sort(key=lambda x: x.name)
            result = []
            for child in children:
                child_path = f"{path}/{child.name}"
                child_dict = {
                    'id': child.id,
                    'name': child.name,
                    'depth': child.depth,
                    'entity': child.entity,
                    'created_by': child.created_by,
                    'updated_by': child.updated_by,
                    'created_at': child.created_at,
                    'updated_at': child.updated_at,
                    'path': child_path,
                    'children': build_nested_dict(child.id, child_path)
                }
                result.append(child_dict)
            return result

        root_path = FOLDER_ROOT_PATH
        tree = {
            'id': None,
            'name': FOLDER_ROOT_NAME,
            'path': root_path,
            'children': build_nested_dict(None, root_path)
        }

        return tree

    # def build_tree(self, folders: List[Folder]) -> Dict:
    #     folder_dict = {}
    #     for folder in folders:
    #         folder_dict[folder.id] = folder
    #     folder.children = []
    #
    #     root_folders = []
    #     for folder in folders:
    #         if folder.parent_id is None:
    #             root_folders.append(folder)
    #         else:
    #             parent_folder = folder_dict.get(folder.parent_id)
    #             if parent_folder:
    #                 parent_folder.children.append(folder)
    #
    #     def build_nested_dict(folder, path):
    #         folder_path = f"{path}/{folder.name}"
    #         folder_dict_repr = {
    #             'id': folder.id,
    #             'name': folder.name,
    #             'depth': folder.depth,
    #             'entity': folder.entity,
    #             'created_by': folder.created_by,
    #             'updated_by': folder.updated_by,
    #             'created_at': folder.created_at,
    #             'updated_at': folder.updated_at,
    #             'path': folder_path,
    #             'children': []
    #         }
    #
    #         folder.children.sort(key=lambda x: x.name)
    #         for child in folder.children:
    #             folder_dict_repr['children'].append(build_nested_dict(child, folder_path))
    #         return folder_dict_repr
    #
    #     root_path = FOLDER_ROOT_PATH
    #     tree = {
    #         'id': 'root',
    #         'name': FOLDER_ROOT_NAME,
    #         'path': root_path,
    #         'children': [build_nested_dict(root, root_path) for root in root_folders]
    #     }
    #
    #     return tree

    def get_folder_tree(self, entity: FolderEntity) -> Dict:
        return self._build_tree(self.get_by_entity(entity))

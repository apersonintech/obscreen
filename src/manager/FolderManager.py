from typing import Dict, Optional, List, Tuple, Union

from src.model.entity.Folder import Folder
from src.model.enum.FolderEntity import FolderEntity, FOLDER_ROOT_PATH, FOLDER_ROOT_NAME
from src.manager.DatabaseManager import DatabaseManager
from src.manager.ContentManager import ContentManager
from src.manager.NodePlayerManager import NodePlayerManager
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

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager,
                 variable_manager: VariableManager):
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

    def get_by(self, query, sort: Optional[str] = None, ascending=True) -> List[Folder]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort, ascending=ascending))

    def get_by_entity(self, entity: FolderEntity) -> List[Folder]:
        return self.get_by("entity = '{}'".format(entity.value))

    def get_children(self, folder: Optional[Folder], entity: Optional[FolderEntity] = None, sort: Optional[str] = None, ascending=True) -> List[Folder]:
        query = " 1=1 "

        if entity:
            query = "{} {}".format(query, "AND entity = '{}'".format(entity.value))

        if folder:
            return self.get_by("parent_id = {} AND {}".format(folder.id, query), sort, ascending)

        return self.get_by("parent_id is null AND {}".format(query), sort, ascending)

    def get_one_by_path(self, path: str, entity: FolderEntity) -> Folder:
        parts = path[1:].split('/')

        result = self._database_manager.execute_read_query("""WITH RECURSIVE FolderCTE AS (
            SELECT id, name, entity, 1 AS depth FROM folder WHERE parent_id IS NULL
            UNION ALL
            SELECT f.id, f.name, f.entity, cte.depth + 1 AS depth FROM folder f
            INNER JOIN FolderCTE cte ON f.parent_id = cte.id
        )
        SELECT id FROM FolderCTE WHERE name = '{}' AND depth = {} AND entity = '{}'
        """.format(parts[-1], len(parts) - 1, entity.value))

        if len(result) > 0:
            return self.get(result[0]['id'])

        return None

    def hydrate_parents(self, folder: Optional[Folder], deep=False) -> Optional[Folder]:
        if not folder:
            return None

        if not folder.parent_id:
            return folder

        parent = self.get(folder.parent_id)
        folder.set_previous(parent)
        return self.hydrate_parents(parent)

    def get_parent_folder(self, folder: Optional[Folder]) -> Optional[Folder]:
        if not folder or not folder.parent_id:
            return None

        return self.get(folder.parent_id)

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

    def get_folders(self, parent_id: Optional[id] = None) -> List[Folder]:
        query = " 1=1 "

        if parent_id:
            query = "{} {}".format(query, "AND parent_id = {}".format(parent_id))

        return self.get_by(query=query)

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

    def move_to_folder(self, entity_id: int, folder_id: int, entity_is_folder=False) -> None:
        folder = self.get(folder_id)

        if not folder and not entity_is_folder:
            return

        if entity_is_folder:
            return self._db.execute_write_query(
                query="UPDATE {} set parent_id = ? WHERE id = ?".format(self.TABLE_NAME),
                params=(folder_id if folder else None, entity_id)
            )

        table = None

        if folder.entity == FolderEntity.CONTENT:
            table = ContentManager.TABLE_NAME
        elif folder.entity == FolderEntity.NODE_PLAYER:
            table = NodePlayerManager.TABLE_NAME

        if table:
            return self._db.execute_write_query(
                query="UPDATE {} set folder_id = ? WHERE id = ?".format(table),
                params=(folder_id, entity_id)
            )

    def get_working_folder(self, entity: FolderEntity) -> str:
        var_name = None
        if entity == FolderEntity.CONTENT:
            var_name = "last_folder_content"
        elif entity == FolderEntity.NODE_PLAYER:
            var_name = "last_folder_node_player"

        if not var_name:
            raise Error("No variable for entity {}".format(entity.value))

        return self.variable_manager.get_one_by_name(var_name).as_string()

    def rename_folder(self, folder_id: int, name: str) -> None:
        folder = self.get(folder_id)

        if not folder:
            return

        self.update_form(folder_id, name)

    def add_folder(self, entity: FolderEntity, name: str, working_folder_path: Optional[str] = None) -> Folder:
        if not working_folder_path:
            working_folder_path = self.get_working_folder(entity)

        working_folder = self.get_one_by_path(path=working_folder_path, entity=entity)
        folder_path = "{}/{}".format(working_folder_path, name)
        parts = folder_path[1:].split('/')

        folder = Folder(
            entity=entity,
            name=name,
            parent_id=working_folder.id if working_folder else None
        )

        self.add_form(folder)
        return folder

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

    def get_folder_tree(self, entity: FolderEntity) -> Dict:
        return self._build_tree(self.get_by_entity(entity))

    def count_subfolders_for_folder(self, folder_id: int) -> int:
        return len(self.get_folders(parent_id=folder_id))

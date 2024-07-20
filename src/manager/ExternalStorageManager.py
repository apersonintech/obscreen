import os
import psutil
import platform
import logging

from typing import Dict, Optional, List, Tuple, Union
from werkzeug.datastructures import FileStorage

from src.model.entity.ExternalStorage import ExternalStorage
from src.util.utils import get_yt_video_id
from src.manager.DatabaseManager import DatabaseManager
from src.manager.LangManager import LangManager
from src.manager.UserManager import UserManager
from src.manager.VariableManager import VariableManager
from src.service.ModelManager import ModelManager
from src.util.UtilFile import randomize_filename


class ExternalStorageManager(ModelManager):

    TABLE_NAME = "external_storage"
    TABLE_MODEL = [
        "uuid CHAR(255)",
        "total_size INTEGER",
        "logical_name TEXT",
        "mount_point TEXT",
        "content_id INTEGER",
        "created_by CHAR(255)",
        "updated_by CHAR(255)",
        "created_at INTEGER",
        "updated_at INTEGER"
    ]

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, user_manager: UserManager, variable_manager: VariableManager):
        super().__init__(lang_manager, database_manager, user_manager, variable_manager)
        self._db = database_manager.open(self.TABLE_NAME, self.TABLE_MODEL)

    def hydrate_object(self, raw_external_storage: dict, id: int = None) -> ExternalStorage:
        if id:
            raw_external_storage['id'] = id

        [raw_external_storage, user_tracker_edits] = self.user_manager.initialize_user_trackers(raw_external_storage)

        if len(user_tracker_edits) > 0:
            self._db.update_by_id(self.TABLE_NAME, raw_external_storage['id'], user_tracker_edits)

        return ExternalStorage(**raw_external_storage)

    def hydrate_list(self, raw_external_storages: list) -> List[ExternalStorage]:
        return [self.hydrate_object(raw_external_storage) for raw_external_storage in raw_external_storages]

    def get(self, id: int) -> Optional[ExternalStorage]:
        object = self._db.get_by_id(self.TABLE_NAME, id)
        return self.hydrate_object(object, id) if object else None

    def get_by(self, query, sort: Optional[str] = None) -> List[ExternalStorage]:
        return self.hydrate_list(self._db.get_by_query(self.TABLE_NAME, query=query, sort=sort))

    def get_one_by(self, query) -> Optional[ExternalStorage]:
        object = self._db.get_one_by_query(self.TABLE_NAME, query=query)

        if not object:
            return None

        return self.hydrate_object(object)

    def get_all(self, sort: Optional[str] = 'created_at', ascending=False) -> List[ExternalStorage]:
        return self.hydrate_list(self._db.get_all(table_name=self.TABLE_NAME, sort=sort, ascending=ascending))

    def get_all_indexed(self, attribute: str = 'id', multiple=False) -> Dict[str, ExternalStorage]:
        index = {}

        for item in self.get_external_storages():
            id = getattr(item, attribute)
            if multiple:
                if id not in index:
                    index[id] = []
                index[id].append(item)
            else:
                index[id] = item

        return index

    def forget_for_user(self, user_id: int):
        external_storages = self.get_by("created_by = '{}' or updated_by = '{}'".format(user_id, user_id))
        edits_external_storages = self.user_manager.forget_user_for_entity(external_storages, user_id)

        for external_storage_id, edits in edits_external_storages.items():
            self._db.update_by_id(self.TABLE_NAME, external_storage_id, edits)

    def get_external_storages(self, content_id: Optional[int] = None) -> List[ExternalStorage]:
        query = " 1=1 "

        if content_id:
            query = "{} {}".format(query, "AND content_id = {}".format(content_id))

        return self.get_by(query=query)

    def pre_add(self, external_storage: Dict) -> Dict:
        self.user_manager.track_user_on_create(external_storage)
        self.user_manager.track_user_on_update(external_storage)
        return external_storage

    def pre_update(self, external_storage: Dict) -> Dict:
        self.user_manager.track_user_on_update(external_storage)
        return external_storage

    def pre_delete(self, external_storage_id: str) -> str:
        return external_storage_id

    def post_add(self, external_storage_id: str) -> str:
        return external_storage_id

    def post_update(self, external_storage_id: str) -> str:
        return external_storage_id

    def post_updates(self):
        pass

    def post_delete(self, external_storage_id: str) -> str:
        return external_storage_id

    def update_form(self, id: int, logical_name: Optional[str] = None, mount_point: Optional[str] = None, content_id: Optional[int] = None, total_size: Optional[int] = None) -> ExternalStorage:
        external_storage = self.get(id)

        if not external_storage:
            return

        form = {
            "total_size": total_size if total_size else external_storage.total_size,
            "logical_name": logical_name if logical_name else external_storage.logical_name,
            "mount_point": mount_point if mount_point else external_storage.mount_point,
            "content_id": content_id if content_id else external_storage.content_id,
        }

        self._db.update_by_id(self.TABLE_NAME, id, self.pre_update(form))
        self.post_update(id)
        return self.get(id)

    def add_form(self, external_storage: Union[ExternalStorage, Dict]) -> None:
        form = external_storage

        if not isinstance(external_storage, dict):
            form = external_storage.to_dict()
            del form['id']

        self._db.add(self.TABLE_NAME, self.pre_add(form))
        self.post_add(external_storage.id)

    def add_form_raw(self, logical_name: Optional[str] = None, mount_point: Optional[str] = None, content_id: Optional[int] = None, total_size: Optional[int] = None) -> ExternalStorage:
        external_storage = ExternalStorage(
            logical_name=logical_name,
            mount_point=mount_point,
            content_id=content_id,
            total_size=total_size,
        )

        self.add_form(external_storage)
        return self.get_one_by(query="uuid = '{}'".format(external_storage.uuid))

    def delete(self, id: int) -> None:
        external_storage = self.get(id)

        if external_storage:
            self.pre_delete(id)
            self._db.delete_by_id(self.TABLE_NAME, id)
            self.post_delete(id)

    def to_dict(self, external_storages: List[ExternalStorage]) -> List[Dict]:
        return [external_storage.to_dict() for external_storage in external_storages]

    @staticmethod
    def list_usb_storage_devices() -> List[ExternalStorage]:
        os_type = platform.system()
        partitions = psutil.disk_partitions()
        removable_devices = []
        for partition in partitions:
            if 'dontbrowse' in partition.opts:
                continue

            if os_type == "Windows":
                if 'removable' in partition.opts:
                    removable_devices.append(partition)
            else:
                if '/media' in partition.mountpoint or '/run/media' in partition.mountpoint or '/mnt' in partition.mountpoint or '/Volumes' in partition.mountpoint:
                    removable_devices.append(partition)

        if not removable_devices:
            return {}

        storages = []

        for device in removable_devices:
            try:
                usage = psutil.disk_usage(device.mountpoint)
                # total_size = usage.total / (1024 ** 3)
                external_storage = ExternalStorage(
                    logical_name=device.device,
                    mount_point=device.mountpoint,
                    content_id=None,
                    total_size=usage.total,
                )
                storages.append(external_storage)
            except Exception as e:
                logging.error(f"Could not retrieve size for device {device.device}: {e}")

        return storages


import json
import sys

from pysondb import PysonDB
from typing import Optional


class DatabaseManager:

    DB_DIR = 'data/db'

    def __init__(self):
        pass

    def open(self, table_name: str, table_model: list) -> PysonDB:
        db_file = "{}/{}.json".format(self.DB_DIR, table_name)
        db = PysonDB(db_file)
        db = self._update_model(db_file, table_model)
        return db

    @staticmethod
    def _update_model(db_file: str, table_model: list) -> Optional[PysonDB]:
        try:
            with open(db_file, 'r') as file:
                db_model = file.read()
                db_model = json.loads(db_model)
                db_model['keys'] = table_model
            with open(db_file, 'w') as file:
                file.write(json.dumps(db_model, indent=4))
                return PysonDB(db_file)
        except FileNotFoundError:
            logging.error("Database file {} not found".format(db_file))
        return None

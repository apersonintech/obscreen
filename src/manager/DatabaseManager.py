import os
import json
import sqlite3
import logging

from sqlite3 import Cursor
from src.utils import wrap_if, is_wrapped_by
from typing import Optional, Dict

class DatabaseManager:

    DB_FILE: str = "data/db/obscreen.db"

    def __init__(self):
        self._conn = None
        self._enabled = True
        self.init()

    def init(self):
        logging.info('Using DB engine {}'.format(self.__class__.__name__))
        self._open()

    def _open(self, flush: bool = False) -> None:
        if flush and os.path.isfile(self.DB_FILE):
            os.unlink(self.DB_FILE)

        self._conn = sqlite3.connect(self.DB_FILE, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def open(self, table_name: str, table_model: list):
        self.execute_write_query('''CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            {}
        )'''.format(table_name, ", ".join(table_model)))

        return self

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_connection(self):
        return self._conn

    def execute_write_query(self, query, params=()) -> None:
        logging.debug(query)
        cur = None
        sanitized_params = []

        for param in params:
            if isinstance(param, bool):
                sanitized_params.append(int(param))
            elif isinstance(param, dict) or isinstance(param, list):
                sanitized_params.append(json.dumps(param))
            else:
                sanitized_params.append(param)

        try:
            with self._conn:
                cur = self._conn.cursor()
                cur.execute(query, tuple(sanitized_params))
        except sqlite3.Error as e:
            logging.error("SQL query execution error while writing '{}': {}".format(query, e))
            self._conn.rollback()
        finally:
            if cur is not None:
                cur.close()

    def execute_read_query(self, query, params=()) -> list:
        logging.debug(query)
        cur = None

        try:
            with self._conn:
                cur = self._conn.cursor()
                cur.execute(query, params)
                rows = cur.fetchall()
                result = [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error("SQL query execution error while reading '{}': {}".format(query, e))
            result = []
        finally:
            if cur is not None:
                cur.close()

        return result

    def get_all(self, table_name: str, sort: Optional[str] = None) -> list:
        return self.execute_read_query(
            query="select * from {} {}".format(table_name, "ORDER BY {} ASC".format(sort) if sort else "")
        )

    def get_by_query(self, table_name: str, query: str = "1=1", sort: Optional[str] = None) -> list:
        return self.execute_read_query(
            query="select * from {} where {} {}".format(
                table_name,
                query,
                "ORDER BY {} ASC".format(sort) if sort else ""
            )
        )

    def get_one_by_query(self, table_name: str, query: str = "1=1", sort: Optional[str] = None) -> list:
        query = "select * from {} where {} {}".format(table_name, query, "ORDER BY {} ASC".format(sort) if sort else "")
        lines = self.execute_read_query(query=query)
        count = len(lines)

        if count > 1:
            raise Error("More than one line returned by query '{}'".format(query))

        return lines[0] if count == 1 else None

    def update_by_query(self, table_name: str, query: str = "1=1", values: dict = {}) -> list:
        return self.execute_write_query(
            query="UPDATE {} SET {} where {}".format(
                table_name,
                " , ".join(["{} = ?".format(k, v) for k, v in values.items()]),
                query
            ),
            params=tuple(v for v in values.values())
        )

    def update_by_id(self, table_name: str, id: int, values: dict = {}) -> list:
        return self.update_by_query(table_name, "id = {}".format(id), values)

    def get_by_id(self, table_name: str, id: int) -> Optional[Dict]:
        return self.get_one_by_query(table_name, "id = {}".format(id))

    def add(self, table_name: str, values: dict) -> None:
        self.execute_write_query(
            query="INSERT INTO {} ({}) VALUES ({})".format(
                table_name,
                ", ".join(["{}".format(key) for key in values.keys()]),
                ", ".join(["?" for _ in values.keys()]),
            ),
            params=tuple(v for v in values.values())
        )

    def delete_by_id(self, table_name: str, id: int) -> None:
        self.execute_write_query("DELETE FROM {} WHERE id = ?".format(table_name), params=(id,))

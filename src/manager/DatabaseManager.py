import os
import re
import json
import sqlite3
import logging

from sqlite3 import Cursor
from src.util.utils import wrap_if, is_wrapped_by
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
        self.pre_migrate()

    def open(self, table_name: str, table_model: list):
        new_table_definition = '''CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            {}
        )'''.format(table_name, ", ".join(table_model))
        self.execute_write_query(new_table_definition)

        old_table_definition = self.execute_read_query("select sql from sqlite_master where tbl_name = ?", (table_name,))
        old_table_definition = old_table_definition[0]['sql']

        delta_queries = self.generate_delta_queries(old_table_definition, new_table_definition)

        for delta_query in delta_queries:
            self.execute_write_query(delta_query)

        return self

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_connection(self):
        return self._conn

    def execute_write_query(self, query, params=(), silent_errors=False) -> None:
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
            if not silent_errors:
                logging.error("SQL query execution error while writing '{}': {}".format(query, e))
            self._conn.rollback()
        except sqlite3.OperationalError:
            pass
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

    def get_all(self, table_name: str, sort: Optional[str] = None, ascending=True) -> list:
        return self.execute_read_query(
            query="select * from {} {}".format(table_name, "ORDER BY {} {}".format(sort, "ASC" if ascending else "DESC") if sort else "")
        )

    def get_by_query(self, table_name: str, query: str = "1=1", sort: Optional[str] = None, values: dict = {}) -> list:
        return self.execute_read_query(
            query="select * from {} where {} {}".format(
                table_name,
                query,
                "ORDER BY {} ASC".format(sort) if sort else ""
            ),
            params=tuple(v for v in values.values())
        )

    def get_one_by_query(self, table_name: str, query: str = "1=1", sort: Optional[str] = None, values: dict = {}) -> list:
        query = "select * from {} where {} {}".format(table_name, query, "ORDER BY {} ASC".format(sort) if sort else "")
        lines = self.execute_read_query(query=query, params=tuple(v for v in values.values()))
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

    @staticmethod
    def parse_create_table_query(query: str):
        table_name_pattern = re.compile(r'CREATE TABLE\s+(IF NOT EXISTS\s+)?["]?(\w+)["]?', re.IGNORECASE)
        columns_pattern = re.compile(r'\((.*)\)', re.DOTALL)

        table_name_match = table_name_pattern.search(query)
        columns_match = columns_pattern.search(query)

        if not table_name_match or not columns_match:
            raise ValueError("Invalid CREATE TABLE query.")

        table_name = table_name_match.group(2)
        columns_part = columns_match.group(1)

        # Split columns_part by commas but ignore commas inside parentheses
        columns = re.split(r',\s*(?![^()]*\))', columns_part)

        # Extract column names and their definitions
        column_definitions = {}
        for column in columns:
            column_parts = column.strip().split(maxsplit=1)
            column_name = column_parts[0]
            column_definition = column.strip()
            column_definitions[column_name] = column_definition

        return table_name, column_definitions


    @staticmethod
    def generate_delta_queries(old_query: str, new_query: str) -> list:
        old_table_name, old_columns = DatabaseManager.parse_create_table_query(old_query)
        new_table_name, new_columns = DatabaseManager.parse_create_table_query(new_query)

        if old_table_name != new_table_name:
            raise ValueError("Table names do not match.")

        old_column_names = set(old_columns.keys())
        new_column_names = set(new_columns.keys())

        columns_to_add = new_column_names - old_column_names
        columns_to_remove = old_column_names - new_column_names

        delta_queries = []

        for column in columns_to_add:
            delta_queries.append(f'ALTER TABLE {old_table_name} ADD COLUMN {new_columns[column]}')

        for column in columns_to_remove:
            delta_queries.append(f'ALTER TABLE {old_table_name} DROP COLUMN {column}')

        return delta_queries

    def pre_migrate(self):
        queries = [
            "DROP TABLE IF EXISTS fleet_studio",
            "ALTER TABLE slideshow RENAME TO slides",
            "DELETE FROM settings WHERE name = 'fleet_studio_enabled'",
            "UPDATE content SET uuid = id WHERE uuid = '' or uuid is null",
        ]

        for query in queries:
            self.execute_write_query(query=query, silent_errors=True)
import json
import logging


class LangManager:

    LANG_FILE = "lang/{}.json"

    def __init__(self, lang: str):
        self._map = {}

        file_name = self.LANG_FILE.format(lang)

        try:
            with open(file_name, 'r') as file:
                self._map = json.load(file)
        except FileNotFoundError:
            logging.error("Lang file {} not found".format(file_name))

    def map(self) -> dict:
        return self._map

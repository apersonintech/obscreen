import json
import logging


class LangManager:

    LANG_FILE = "lang/{}.json"

    def __init__(self, lang: str):
        self._map = {}
        self._lang = lang
        self.load()

    def load(self, directory: str = "", prefix: str = ""):
        file_name = "{}{}{}".format(directory, "/" if directory else "", self.LANG_FILE.format(self._lang))

        try:
            with open(file_name, 'r') as file:
                for key, value in json.load(file).items():
                    self._map["{}{}{}".format(prefix, "_" if prefix else "", key)] = value
        except FileNotFoundError:
            logging.error("Lang file {} not found".format(file_name))

    def map(self) -> dict:
        return self._map

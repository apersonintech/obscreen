
class Selectable:

    def __init__(self, key: str = '', label: str = ''):
        self._key = key
        self._label = label

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = value

    def __str__(self) -> str:
        return f"Selectable(" \
               f"key='{self.key}',\n" \
               f"label='{self.label}',\n" \
               f")"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label
        }

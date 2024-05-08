from enum import Enum


class SlideInputType(Enum):

    UPLOAD = 'upload'
    TEXT = 'text'

    @staticmethod
    def is_editable(value: Enum) -> bool:
        if value == SlideInputType.UPLOAD:
            return False
        elif value == SlideInputType.TEXT:
            return True


class SlideType(Enum):

    PICTURE = 'picture'
    YOUTUBE = 'youtube'
    VIDEO = 'video'
    URL = 'url'

    @staticmethod
    def get_input(value: Enum) -> SlideInputType:
        if value == SlideType.PICTURE:
            return SlideInputType.UPLOAD
        elif value == SlideType.VIDEO:
            return SlideInputType.UPLOAD
        elif value == SlideType.YOUTUBE:
            return SlideInputType.TEXT
        elif value == SlideType.URL:
            return SlideInputType.TEXT

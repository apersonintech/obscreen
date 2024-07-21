import mimetypes

from enum import Enum
from typing import Union, List, Optional

from src.util.utils import str_to_enum

AUTO_DURATION_CHEATCODE = 98769876


class ContentInputType(Enum):

    UPLOAD = 'upload'
    TEXT = 'text'
    STORAGE = 'storage'

    @staticmethod
    def is_editable(value: Enum) -> bool:
        if value == ContentInputType.UPLOAD:
            return False
        elif value == ContentInputType.TEXT:
            return True
        elif value == ContentInputType.STORAGE:
            return True


class ContentType(Enum):

    EXTERNAL_STORAGE = 'external_storage'
    PICTURE = 'picture'
    URL = 'url'
    YOUTUBE = 'youtube'
    VIDEO = 'video'

    @staticmethod
    def guess_content_type_file(filename: str):
        mime_type, _ = mimetypes.guess_type(filename)

        if mime_type in [
            'image/gif',
            'image/png',
            'image/jpeg',
            'image/webp',
            'image/jpg'
        ]:
            return ContentType.PICTURE
        elif mime_type in [
            'video/mp4'
        ]:
            return ContentType.VIDEO

        return None

    @staticmethod
    def get_input(value: Enum) -> ContentInputType:
        if value == ContentType.PICTURE:
            return ContentInputType.UPLOAD
        elif value == ContentType.VIDEO:
            return ContentInputType.UPLOAD
        elif value == ContentType.YOUTUBE:
            return ContentInputType.TEXT
        elif value == ContentType.URL:
            return ContentInputType.TEXT
        elif value == ContentType.EXTERNAL_STORAGE:
            return ContentInputType.STORAGE

    @staticmethod
    def get_fa_icon(value: Union[Enum, str]) -> str:
        if isinstance(value, str):
            value = str_to_enum(value, ContentType)

        if value == ContentType.PICTURE:
            return 'fa-regular fa-image'
        elif value == ContentType.VIDEO:
            return 'fa-video-camera'
        elif value == ContentType.YOUTUBE:
            return 'fa-brands fa-youtube'
        elif value == ContentType.URL:
            return 'fa-link'
        elif value == ContentType.EXTERNAL_STORAGE:
            return 'fa-brands fa-usb'

        return 'fa-file'

    @staticmethod
    def get_color_icon(value: Enum) -> str:
        if isinstance(value, str):
            value = str_to_enum(value, ContentType)

        if value == ContentType.PICTURE:
            return 'info'
        elif value == ContentType.VIDEO:
            return 'success-alt'
        elif value == ContentType.YOUTUBE:
            return 'youtube'
        elif value == ContentType.URL:
            return 'danger'
        elif value == ContentType.EXTERNAL_STORAGE:
            return 'other'

        return 'neutral'

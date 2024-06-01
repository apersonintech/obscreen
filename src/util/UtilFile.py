import os
import uuid
import math


def randomize_filename(old_filename: str) -> str:
    new_uuid = str(uuid.uuid4())
    _, extension = os.path.splitext(old_filename)
    return f"{new_uuid}{extension}"


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

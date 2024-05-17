import os
import re
import logging
import subprocess
import platform


from typing import Optional, List, Dict
from enum import Enum
from cron_descriptor import ExpressionDescriptor
from cron_descriptor.Exception import FormatException, WrongArgumentException, MissingFieldException

CAMEL_CASE_TO_SNAKE_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')


def am_i_in_docker():
    docker_env = os.path.exists('/.dockerenv')
    docker_cgroup = False
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            for line in f:
                if 'docker' in line:
                    docker_cgroup = True
                    break
    except Exception:
        pass

    return docker_env or docker_cgroup


def enum_to_dict(enum_class) -> Dict:
    values = {}

    for enum_item in enum_class:
        values[enum_item.value] = enum_item.value

    return values


def camel_to_snake(camel: str) -> str:
    return CAMEL_CASE_TO_SNAKE_CASE_PATTERN.sub('_', camel).lower()


def is_validate_cron_date_time(expression) -> bool:
    pattern = re.compile(r'^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\*\s+(\d+)$')
    return bool(pattern.match(expression))


def get_safe_cron_descriptor(expression: str, use_24hour_time_format=True, locale_code: Optional[str] = None) -> str:
    if is_validate_cron_date_time(expression):
        [minutes, hours, day, month, _, year] = expression.split(' ')
        return "{}-{}-{} at {}:{}".format(
            year,
            month.zfill(2),
            day.zfill(2),
            hours.zfill(2),
            minutes.zfill(2)
        )

    options = {
        "expression": expression,
        "use_24hour_time_format": use_24hour_time_format
    }

    if locale_code:
        options["locale_code"] = locale_code
    try:
        return str(ExpressionDescriptor(**options))
    except FormatException:
        return ''
    except WrongArgumentException:
        return ''
    except MissingFieldException:
        return ''


def get_optional_string(var: Optional[str]) -> Optional[str]:
    if var is None:
        return None

    var = var.strip()

    if var:
        return var

    return None


def get_keys(dict_or_object, key_list_name: str, key_attr_name: str = 'key') -> Optional[List]:
    if dict_or_object is None:
        return None

    is_dict = isinstance(dict_or_object, dict)
    is_object = not is_dict and isinstance(dict_or_object, object)

    if is_dict:
        iterable = dict_or_object[key_list_name]
        if iterable is None:
            return None
        return [item[key_attr_name] for item in iterable]

    if is_object:
        iterable = getattr(dict_or_object, key_list_name)
        if iterable is None:
            return None
        return [getattr(item, key_attr_name) for item in iterable]

    return None


def enum_to_str(enum: Optional[Enum]) -> Optional[str]:
    if enum:
        return str(enum.value)

    return None


def str_to_enum(str_val: str, enum_class) -> Enum:
    for enum_item in enum_class:
        if enum_item.value == str_val:
            return enum_item
    raise ValueError(f"{str_val} is not a valid {enum_class.__name__} item")


def get_ip_address() -> Optional[str]:
    try:
        os_name = platform.system().lower()
        if os_name == "linux":
            result = subprocess.run(["ip", "-4", "route", "get", "8.8.8.8"], capture_output=True, text=True)
            ip_address = result.stdout.split()[6]
        elif os_name == "darwin":
            result = subprocess.run(
                ["ipconfig", "getifaddr", "en0"], capture_output=True, text=True)
            ip_address = result.stdout.strip()
        elif os_name == "windows":
            result = subprocess.run(["ipconfig"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            ip_address = None
            for line in lines:
                if "ipv4 address" in line.lower():
                    ip_address = line.split(': ')[1].strip()
                    break
        else:
            logging.warn(f"Unsupported OS: {os_name}")
            return None
        return ip_address
    except Exception as e:
        logging.error(f"Error obtaining IP address: {e}")
        return None


def regex_search(pattern: str, string: str, group: int):
    """Shortcut method to search a string for a given pattern.
    :param str pattern:
        A regular expression pattern.
    :param str string:
        A target string to search.
    :param int group:
        Index of group to return.
    :rtype:
        str or tuple
    :returns:
        Substring pattern matches.
    """
    regex = re.compile(pattern)
    results = regex.search(string)
    if not results:
        return False

    return results.group(group)


def get_yt_video_id(url: str) -> str:
    if len(url) <= 14:
        return url

    """Extract the ``video_id`` from a YouTube url.
    This function supports the following patterns:
    - :samp:`https://youtube.com/watch?v={video_id}`
    - :samp:`https://youtube.com/embed/{video_id}`
    - :samp:`https://youtu.be/{video_id}`
    :param str url:
        A YouTube url containing a video id.
    :rtype: str
    :returns:
        YouTube video id.
    """
    return regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url, group=1)

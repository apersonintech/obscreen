import re
import subprocess
import platform

from typing import Optional, List
from enum import Enum
from cron_descriptor import ExpressionDescriptor
from cron_descriptor.Exception import FormatException, WrongArgumentException, MissingFieldException


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
        print(enum)
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
            result = subprocess.run(
                ["ip", "-4", "route", "get", "8.8.8.8"],
                capture_output=True,
                text=True
            )
            ip_address = result.stdout.split()[6]
        elif os_name == "darwin":
            result = subprocess.run(
                ["ipconfig", "getifaddr", "en0"],
                capture_output=True,
                text=True
            )
            ip_address = result.stdout.strip()
        elif os_name == "windows":
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            ip_address = None
            for line in lines:
                if "ipv4 address" in line.lower():
                    ip_address = line.split(': ')[1].strip()
                    break
        else:
            print(f"Unsupported OS: {os_name}")
            return None
        return ip_address
    except Exception as e:
        print(f"Error obtaining IP address: {e}")
        return None


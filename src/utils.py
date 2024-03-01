import re
import subprocess
import platform

from typing import Optional
from enum import Enum


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


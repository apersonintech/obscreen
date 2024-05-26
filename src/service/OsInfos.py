import os
import platform
import psutil
import socket

from src.utils import convert_size


def get_rpi_model():
    try:
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as file:
                model = file.read().strip()
            return model
        else:
            return "Not a Raspberry Pi or model information not available."
    except Exception as e:
        return f"Error retrieving RPi model: {e}"


def get_free_space():
    try:
        usage = psutil.disk_usage('/')
        return convert_size(usage.free)
    except Exception as e:
        return f"Error retrieving free space: {e}"


def get_memory_usage():
    try:
        memory_info = psutil.virtual_memory()
        return {
            'total': convert_size(memory_info.total),
            'available': convert_size(memory_info.available),
            'percent': memory_info.percent,
            'used': convert_size(memory_info.used),
            'free': convert_size(memory_info.free)
        }
    except Exception as e:
        return f"Error retrieving memory usage: {e}"


def get_network_info():
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for iface, addr_list in addrs.items():
            if stats[iface].isup:
                mac_address = None
                ip_address = None
                for addr in addr_list:
                    if addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                    elif addr.family == socket.AF_INET:
                        ip_address = addr.address
                if mac_address and ip_address:
                    return {
                        'interface': iface,
                        'mac_address': mac_address,
                        'ip_address': ip_address
                    }
        return "No active network interface found."
    except Exception as e:
        return f"Error retrieving network information: {e}"


def get_os_version():
    try:
        return platform.platform()
    except Exception as e:
        return f"Error retrieving OS version: {e}"


def get_last_lines_of_logs(logfile, lines):
    try:
        if not os.path.exists(logfile):
            return f"Log file {logfile} does not exist."
        with open(logfile, 'r') as file:
            logs = file.readlines()
            return ''.join(logs[-lines:])
    except Exception as e:
        return f"Error retrieving log lines: {e}"


def get_default_log_file():
    os_type = platform.system()
    if os_type == 'Linux':
        return '/var/log/syslog'
    elif os_type == 'Darwin':  # macOS
        return '/var/log/system.log'
    elif os_type == 'Windows':
        return 'C:\\Windows\\System32\\LogFiles\\WMI\\SysEvent.evt'
    else:
        return None


def get_all():
    infos = {}
    network_info = get_network_info()

    if isinstance(network_info, dict):
        infos["Network Interface"] = network_info['interface']
        infos["MAC Address"] = network_info['mac_address']
        infos["IP Address"] = network_info['ip_address']

    return {
        "Raspberry Pi Model": get_rpi_model(),
        "Storage Free Space": get_free_space(),
        "Memory Usage": get_memory_usage(),
        "OS Version": get_os_version(),
    }

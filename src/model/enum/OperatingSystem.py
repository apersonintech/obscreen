from enum import Enum


class OperatingSystem(Enum):

    RASPBIAN = 'raspbian'
    WINDOWS = 'windows'
    MACOS = 'macos'
    DEBIAN = 'debian'
    FEDORA = 'fedora'
    UBUNTU = 'ubuntu'
    SUSE = 'suse'
    REDHAT = 'redhat'
    CENTOS = 'centos'
    OTHER = 'other'

    @staticmethod
    def get_fa_icon(value: Enum) -> str:
        if value == OperatingSystem.RASPBIAN:
            return 'fa-brands fa-raspberry-pi'
        elif value == OperatingSystem.WINDOWS:
            return 'fa-brands fa-windows'
        elif value == OperatingSystem.MACOS:
            return 'fa-brands fa-apple'
        elif value == OperatingSystem.DEBIAN:
            return 'fa-brands fa-debian'
        elif value == OperatingSystem.FEDORA:
            return 'fa-brands fa-fedora'
        elif value == OperatingSystem.UBUNTU:
            return 'fa-brands fa-ubuntu'
        elif value == OperatingSystem.SUSE:
            return 'fa-brands fa-suse'
        elif value == OperatingSystem.REDHAT:
            return 'fa-brands fa-redhat'
        elif value == OperatingSystem.CENTOS:
            return 'fa-brands fa-centos'
        elif value == OperatingSystem.OTHER:
            return 'fa-display'

        return 'fa-server'

    def get_color_icon(value: Enum) -> str:
        if value == OperatingSystem.RASPBIAN:
            return 'raspbian'
        elif value == OperatingSystem.WINDOWS:
            return 'windows'
        elif value == OperatingSystem.MACOS:
            return 'macos'
        elif value == OperatingSystem.DEBIAN:
            return 'debian'
        elif value == OperatingSystem.FEDORA:
            return 'fedora'
        elif value == OperatingSystem.UBUNTU:
            return 'ubuntu'
        elif value == OperatingSystem.SUSE:
            return 'suse'
        elif value == OperatingSystem.REDHAT:
            return 'redhat'
        elif value == OperatingSystem.CENTOS:
            return 'centos'
        elif value == OperatingSystem.OTHER:
            return 'other'

        return 'white'

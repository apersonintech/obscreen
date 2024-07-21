import os
import psutil
import platform
import logging
import http.server
import socketserver
import os
import signal
import sys
import socket
import threading

from typing import Dict, Optional, List, Tuple, Union
from pathlib import Path

from src.service.ModelStore import ModelStore
from src.model.entity.ExternalStorage import ExternalStorage


class ExternalStorageServer:

    def __init__(self, kernel, model_store: ModelStore):
        self._kernel = kernel
        self._model_store = model_store

    def get_directory(self):
        return self._model_store.config().map().get('chroot_http_external_storage').replace(
            '%application_dir%', self._kernel.get_application_dir()
        )

    def get_port(self) -> Optional[int]:
        port = self._model_store.config().map().get('port_http_external_storage')
        return int(port) if port else None

    def run(self):
        port = self.get_port()
        bind = self._model_store.config().map().get('bind_http_external_storage')
        if not port:
            return

        thread = threading.Thread(target=self._start, args=(self.get_directory(), port, bind))
        thread.daemon = True
        thread.start()

    def _start(self, directory, port, bind):
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

        Handler = CustomHTTPRequestHandler

        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        with ReusableTCPServer((bind, port), Handler) as httpd:
            logging.info("Serving external storage on path>{}:{}".format(directory, port))
            httpd.serve_forever()

    @staticmethod
    def list_usb_storage_devices() -> List[ExternalStorage]:
        os_type = platform.system()
        partitions = psutil.disk_partitions()
        removable_devices = []
        for partition in partitions:
            if 'dontbrowse' in partition.opts:
                continue

            if os_type == "Windows":
                if 'removable' in partition.opts:
                    removable_devices.append(partition)
            else:
                if '/media' in partition.mountpoint or '/run/media' in partition.mountpoint or '/mnt' in partition.mountpoint or '/Volumes' in partition.mountpoint:
                    removable_devices.append(partition)

        if not removable_devices:
            return {}

        storages = []

        for device in removable_devices:
            try:
                usage = psutil.disk_usage(device.mountpoint)
                # total_size = usage.total / (1024 ** 3)
                external_storage = ExternalStorage(
                    logical_name=device.device,
                    mount_point=device.mountpoint,
                    content_id=None,
                    total_size=usage.total,
                )
                storages.append(external_storage)
            except Exception as e:
                logging.error(f"Could not retrieve size for device {device.device}: {e}")

        return storages


    @staticmethod
    def get_external_storage_devices():
        return {storage.mount_point: "{} ({} - {}GB)".format(
            storage.mount_point,
            storage.logical_name,
            storage.total_size_in_gigabytes()
        ) for storage in ExternalStorageServer.list_usb_storage_devices()}
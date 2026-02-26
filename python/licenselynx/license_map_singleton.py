#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
import sys
from importlib import resources
from threading import Lock
from licenselynx.license_map import _LicenseMap
from licenselynx.license_object import LicenseObject


class _Singleton(type):
    _instances: dict[type, type] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class _LicenseMapSingleton(metaclass=_Singleton):
    def __init__(self):
        self._file_path = resources.files("licenselynx.resources").joinpath("merged_data.json")
        try:
            with self._file_path.open() as file:
                data = json.load(file)

                license_maps = {}
                for map_key, map_data in data.items():
                    if map_key.endswith("Map"):
                        org_map = {}
                        for lic_name, lic_data in map_data.items():
                            org_map[lic_name] = LicenseObject(**lic_data)
                        license_maps[map_key] = org_map

                self._merged_data = _LicenseMap(license_maps)
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

    @property
    def merged_data(self) -> _LicenseMap:
        return self._merged_data

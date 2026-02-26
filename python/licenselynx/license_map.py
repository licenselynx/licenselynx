#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
from dataclasses import dataclass

from typing import Optional
from licenselynx.license_object import LicenseObject
from licenselynx.extra import Extra


@dataclass
class _LicenseMap(object):
    license_maps: dict[str, dict[str, LicenseObject]]

    def get_canonical_map(self) -> dict[str, LicenseObject]:
        return self.license_maps.get("stableMap", {})

    def get_risky_map(self) -> dict[str, LicenseObject]:
        return self.license_maps.get("riskyMap", {})

    def get_map(self, extra: Optional[Extra]) -> Optional[dict[str, LicenseObject]]:
        if extra is None:
            return self.get_canonical_map()
        return self.license_maps.get(f"{extra.value}Map")

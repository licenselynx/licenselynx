#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import sys
from typing import Optional
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import _LicenseMapSingleton
from licenselynx.quotes_handler import _QuotesHandler
from licenselynx.extra import Extra


class LicenseLynx:

    @staticmethod
    def map(license_name: str, risky: bool = False, extra: Optional[Extra] = None) -> Optional[LicenseObject]:
        """
        Maps license name to the canonical license identifier
        :param license_name: string of a license name
        :param risky: enable risky mappings
        :param extra: enable extra mappings for a specific company/org
        :return: LicenseObject with the canonical license identifier and source, None if no license is found,
        or throws an exception if a runtime error occurs
        """
        try:
            license_name = _QuotesHandler().normalize_quotes(license_name)
            instance = _LicenseMapSingleton()

            license_object: Optional[LicenseObject] = instance.merged_data.get_canonical_map().get(license_name)

            if not license_object and risky:
                license_object = instance.merged_data.get_risky_map().get(license_name)

            if not license_object and extra:
                extra_map = instance.merged_data.get_map(extra)
                if extra_map:
                    license_object = extra_map.get(license_name)

            return license_object
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

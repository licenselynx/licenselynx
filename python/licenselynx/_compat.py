#
# SPDX-FileCopyrightText: Copyright 2026 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        """String enum behavior for our explicitly valued enums on Python 3.9/3.10."""

        __str__ = str.__str__
        __format__ = str.__format__

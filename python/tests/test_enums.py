#
# SPDX-FileCopyrightText: Copyright 2026 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json

import pytest

from licenselynx import LicenseSource, Organization


@pytest.mark.parametrize("member,value", [
    (Organization.SIEMENS, "siemens"),
    (LicenseSource.SPDX, "spdx"),
    (LicenseSource.SCANCODE_LICENSEDB, "scancode-licensedb"),
    (LicenseSource.CUSTOM, "custom"),
])
def test_enum_string_interoperability(member, value):
    """Preserve the public string behavior across native and fallback enums."""
    assert isinstance(member, str)
    assert member == value
    assert str(member) == value
    assert f"{member}" == value
    assert format(member, ">24") == format(value, ">24")
    assert {value: "found"}[member] == "found"
    assert json.loads(json.dumps({member: member})) == {value: value}
    assert type(member)(value) is member

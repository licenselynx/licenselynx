#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
from pathlib import Path

import pytest
from licenselynx import LicenseLynx, Organization

SPEC = json.loads((Path(__file__).resolve().parents[2] / "fixtures" / "normalization.json").read_text("utf-8"))


@pytest.mark.smoke
@pytest.mark.parametrize("case", SPEC["mappingCases"], ids=lambda case: case["name"])
def test_shared_case_insensitive_mappings(case):
    org = Organization(case["org"]) if "org" in case else None
    result = LicenseLynx.map(case["input"], risky=case.get("risky", False), org=org)
    if case["id"] is None:
        assert result is None
    else:
        assert result is not None
        assert result.id == case["id"]
        assert result.src == case["src"]


@pytest.mark.smoke
def test_stable_map_lookup():
    """Stable map lookup for a well-known SPDX identifier."""
    result = LicenseLynx.map("0BSD")
    assert result is not None, "Expected a result for '0BSD'"
    assert result.id == "0BSD"


@pytest.mark.smoke
def test_risky_map_lookup_with_flag():
    """Risky map entry resolves when risky=True."""
    result = LicenseLynx.map("LIbpng License v2", risky=True)
    assert result is not None, "Expected a result for 'LIbpng License v2' with risky=True"
    assert result.id == "libpng-2.0"


@pytest.mark.smoke
def test_risky_entry_not_resolved_without_flag():
    """Risky map entry must NOT resolve without the risky flag."""
    result = LicenseLynx.map("LIbpng License v2")
    assert result is None, "Expected None for 'LIbpng License v2' without risky=True"


@pytest.mark.smoke
def test_organization_scoped_lookup():
    """Organization-scoped lookup resolves with correct id and src."""
    result = LicenseLynx.map("Siemens Inner Source License v1.5", org=Organization.SIEMENS)
    assert result is not None, "Expected a result for org=Organization.SIEMENS"
    assert result.id == "SISL-1.5"
    assert result.src == "siemens"


@pytest.mark.smoke
def test_organization_entry_not_resolved_without_org():
    """Organization entry must NOT resolve without the org parameter."""
    result = LicenseLynx.map("Siemens Inner Source License v1.5")
    assert result is None, "Expected None without org parameter"

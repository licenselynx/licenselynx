#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
from pathlib import Path

import pytest
from licenselynx.licenselynx import _normalize_license_name

SPEC = json.loads(
    (Path(__file__).resolve().parents[2] / "fixtures" / "normalization.json").read_text(
        "utf-8"
    )
)


@pytest.mark.parametrize("case", SPEC["testCases"], ids=lambda c: c["name"])
def test_cases(case):
    assert _normalize_license_name(case["input"]) == case["expected"]


@pytest.mark.parametrize(
    "quote", SPEC["quoteCharacters"], ids=lambda c: f"U+{ord(c):04X}"
)
def test_every_quote_character_is_replaced(quote):
    assert _normalize_license_name(f"a{quote}b") == f"a{SPEC['quoteReplacement']}b"


@pytest.mark.parametrize(
    "char", SPEC["trimCharacters"], ids=lambda c: f"U+{ord(c):04X}"
)
def test_every_trim_character_is_trimmed(char):
    assert _normalize_license_name(f"{char}a{char}") == "a"

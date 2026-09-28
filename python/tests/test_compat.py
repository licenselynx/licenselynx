#
# SPDX-FileCopyrightText: Copyright 2026 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import copy
import enum
import importlib.util
import json
import sys

import pytest

from licenselynx import _compat


@pytest.fixture(params=[
    pytest.param((3, 9), id="fallback-3.9"),
    pytest.param((3, 10), id="fallback-3.10"),
    pytest.param(sys.version_info, id="native", marks=pytest.mark.skipif(
        sys.version_info < (3, 11), reason="Native StrEnum requires Python 3.11+",
    )),
])
def str_enum(request, monkeypatch):
    """Execute both branches without reloading the module used by public enums."""
    spec = importlib.util.spec_from_file_location("_compat_under_test", _compat.__file__)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with monkeypatch.context() as patch:
        patch.setattr(sys, "version_info", request.param)
        spec.loader.exec_module(module)
    if request.param >= (3, 11):
        assert module.StrEnum is getattr(enum, "StrEnum")
    return module.StrEnum


@pytest.fixture
def identifiers(str_enum):
    class Identifier(str_enum):
        LICENSE = "License-ID"
        ALIAS = "License-ID"
        UNICODE = "Lizenz-ä"
        EMPTY = ""

    return Identifier


@pytest.mark.parametrize("value", ["License-ID", "Lizenz-ä", ""])
def test_explicit_values_remain_strings(identifiers, value):
    member = identifiers(value)
    assert isinstance(member, str)
    assert isinstance(member, enum.Enum)
    assert member.value == value
    assert str(member) == value
    assert member == value
    assert member.upper() == value.upper()
    assert bool(member) == bool(value)


@pytest.mark.parametrize("spec", ["", ">20", "*^24", ".4"])
def test_formatting_uses_value_instead_of_enum_name(identifiers, spec):
    member = identifiers.LICENSE
    assert f"{member}" == "License-ID"
    assert format(member, spec) == format(member.value, spec)


def test_string_keys_are_interchangeable(identifiers):
    member = identifiers.LICENSE
    assert hash(member) == hash(member.value)
    assert {member: "found"}[member.value] == "found"
    assert {member.value: "found"}[member] == "found"
    assert len({member, member.value}) == 1


def test_json_serializes_values_and_keys(identifiers):
    payload = {identifiers.LICENSE: [identifiers.UNICODE, identifiers.EMPTY]}
    assert json.loads(json.dumps(payload)) == {"License-ID": ["Lizenz-ä", ""]}


def test_lookup_aliases_and_iteration(identifiers):
    assert identifiers["LICENSE"] is identifiers.LICENSE
    assert identifiers("License-ID") is identifiers.LICENSE
    assert identifiers.ALIAS is identifiers.LICENSE
    assert identifiers.ALIAS.name == "LICENSE"
    assert list(identifiers) == [identifiers.LICENSE, identifiers.UNICODE, identifiers.EMPTY]


def test_unknown_identifiers_are_rejected(identifiers):
    with pytest.raises(ValueError):
        identifiers("license-id")
    with pytest.raises(KeyError):
        identifiers["UNKNOWN"]


def test_copy_preserves_enum_identity(identifiers):
    assert copy.copy(identifiers.LICENSE) is identifiers.LICENSE
    assert copy.deepcopy(identifiers.LICENSE) is identifiers.LICENSE

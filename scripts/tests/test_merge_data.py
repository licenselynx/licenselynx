#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import os
import tempfile
from pathlib import Path

import pytest
from src.load.merge_data import (
    read_data, write_data, main, _build_maps_from_dir, read_org_data, merge_data_to_paths, normalize_license_name
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((REPO_ROOT / "fixtures" / "normalization.json").read_text("utf-8"))


@pytest.mark.parametrize("case", SPEC["testCases"], ids=lambda case: case["name"])
def test_shared_normalization_cases(case):
    assert normalize_license_name(case["input"]) == case["expected"]


@pytest.mark.parametrize("quote", SPEC["quoteCharacters"])
def test_shared_quote_characters(quote):
    assert normalize_license_name(f"A{quote}B") == "a'b"


@pytest.mark.parametrize("char", SPEC["trimCharacters"])
def test_shared_trim_characters(char):
    assert normalize_license_name(char + "MIT" + char) == "mit"


@pytest.fixture(scope="module")
def repository_maps():
    data = read_data(str(REPO_ROOT / "data"))
    data.update(read_org_data(str(REPO_ROOT / "data")))
    return data


@pytest.mark.parametrize("case", SPEC["mappingCases"], ids=lambda case: case["name"])
def test_shared_case_insensitive_mappings(repository_maps, case):
    key = normalize_license_name(case["input"])
    result = repository_maps["stableMap"].get(key)
    if result is None and case.get("risky", False):
        result = repository_maps["riskyMap"].get(key)
    if result is None and "org" in case:
        result = repository_maps[case["org"]].get(key)
    if case["id"] is None:
        assert result is None
    else:
        assert result == {"id": case["id"], "src": case["src"]}


@pytest.fixture
def data_dir(tmpdir):
    data = {
        "license1.json": {"canonical": {"id": "license1"}, "aliases": {"SPDX": ["lic1"], "custom": ["lic1_custom"]},
                          "risky": ["lic1_risky"]},
        "license2.json": {"canonical": {"id": "license2"}, "aliases": {"SPDX": ["lic2", "lic2_alt"]}}
    }
    for filename, content in data.items():
        filepath = tmpdir.join(filename)
        with open(filepath, 'w') as f:
            json.dump(content, f)
    return tmpdir


def test_read_data(data_dir):
    data = read_data(str(data_dir))
    print(data)
    assert len(data) == 2
    stable_map = "stableMap"
    assert len(data[stable_map]) == 6
    risky_map = "riskyMap"
    assert len(data[risky_map]) == 1

    assert "license1" in data[stable_map]
    assert "lic1" in data[stable_map]
    assert "lic1_custom" in data[stable_map]

    assert "license2" in data[stable_map]
    assert "lic2" in data[stable_map]
    assert "lic2_alt" in data[stable_map]

    assert "lic1_risky" in data[risky_map]


def test_write_data(tmpdir):
    alias_mapping = {"license1": "license1", "lic1": "license1"}
    output_path = tmpdir.join("test_output.json")
    write_data(alias_mapping, str(output_path))
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data == alias_mapping


@pytest.fixture
def temp_data_dir():
    # Create a temporary directory with JSON files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample JSON files
        license_1 = {
            "canonical": {
                "id": "MIT",
                "src": "spdx"
            },
            "aliases": {
                "source1": ["MIT License", "MIT Open Source License"],
                "source2": ["MIT"]
            },
        }

        license_2 = {
            "canonical": {
                "id": "GPL",
                "src": "spdx",
            },
            "aliases": {
                "source1": ["GNU General Public License", "GPL v3"],
                "source2": ["GPLv3"]
            },
            "risky": [
                "risky_gpl_3"
            ]
        }

        # Write the JSON data to file in the temp directory
        with open(os.path.join(temp_dir, 'license1.json'), 'w') as f:
            json.dump(license_1, f)

        with open(os.path.join(temp_dir, 'license2.json'), 'w') as f:
            json.dump(license_2, f)

        yield temp_dir  # This is the data directory


@pytest.fixture
def temp_output_file():
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        yield temp_file.name
    # Clean up after the test
    os.remove(temp_file.name)


def test_main_integration(temp_data_dir, temp_output_file, monkeypatch):
    # Mock the command-line arguments
    monkeypatch.setattr('sys.argv', ['data_validation', '--output', temp_output_file])

    # Set the DATA_DIR variable to the temporary data directory for testing
    monkeypatch.setattr('src.load.merge_data.DATA_DIR', temp_data_dir)

    # Call the main function
    main()

    # Check the output file contents
    with open(temp_output_file, 'r') as f:
        output_data = json.load(f)

    # Expected alias mappings
    expected_output = {
        "stableMap": {
            "mit": {
                "id": "MIT",
                "src": "spdx"
            },
            "mit license": {
                "id": "MIT",
                "src": "spdx"
            },
            "mit open source license": {
                "id": "MIT",
                "src": "spdx"
            },
            "gnu general public license": {
                "id": "GPL",
                "src": "spdx"
            },
            "gpl v3": {
                "id": "GPL",
                "src": "spdx"
            },
            "gplv3": {
                "id": "GPL",
                "src": "spdx"
            },
            "gpl": {
                "id": "GPL",
                "src": "spdx"
            },
        },
        'riskyMap': {
            "risky_gpl_3": {
                "id": "GPL",
                "src": "spdx"
            }
        }
    }

    assert output_data == expected_output


def test_build_maps_from_dir(tmpdir):
    license1 = {
        "canonical": {"id": "MIT"},
        "aliases": {"spdx": ["MIT License"]},
        "risky": ["mit-risky"]
    }
    license2 = {
        "canonical": {"id": "Apache-2.0"},
        "aliases": {"spdx": ["Apache License 2.0"], "custom": ["Apache2"]},
        "risky": ["apache-risky"]
    }
    with open(tmpdir.join("MIT.json"), 'w') as f:
        json.dump(license1, f)
    with open(tmpdir.join("Apache-2.0.json"), 'w') as f:
        json.dump(license2, f)

    canonical_dict, risky_dict = _build_maps_from_dir(str(tmpdir))

    # Canonical IDs present
    assert "mit" in canonical_dict
    assert "apache-2.0" in canonical_dict

    # Aliases present
    assert "mit license" in canonical_dict
    assert "apache license 2.0" in canonical_dict
    assert "apache2" in canonical_dict

    # Canonical dict maps to correct objects
    assert canonical_dict["mit"] == {"id": "MIT"}
    assert canonical_dict["mit license"] == {"id": "MIT"}
    assert canonical_dict["apache-2.0"] == {"id": "Apache-2.0"}

    # Risky entries
    assert "mit-risky" in risky_dict
    assert risky_dict["mit-risky"] == {"id": "MIT"}
    assert "apache-risky" in risky_dict
    assert risky_dict["apache-risky"] == {"id": "Apache-2.0"}


def test_build_maps_from_dir_skips_non_json(tmpdir):
    license1 = {
        "canonical": {"id": "MIT"},
        "aliases": {"spdx": ["MIT License"]},
        "risky": []
    }
    with open(tmpdir.join("MIT.json"), 'w') as f:
        json.dump(license1, f)
    with open(tmpdir.join("README.txt"), 'w') as f:
        f.write("This is not a JSON file")

    canonical_dict, risky_dict = _build_maps_from_dir(str(tmpdir))

    # Only JSON file processed
    assert "mit" in canonical_dict
    assert "mit license" in canonical_dict
    assert len(canonical_dict) == 2
    assert len(risky_dict) == 0


def test_read_org_data_single_org(tmpdir):
    org_dir = tmpdir.mkdir("orgs").mkdir("testOrg")
    license1 = {
        "canonical": {"id": "testOrgId", "src": "testOrg"},
        "aliases": {"custom": ["testOrg License"]},
        "isMajorVersionOnly": False,
        "rejected": [],
        "risky": ["testOrg-risky"]
    }
    with open(org_dir.join("testOrgId.json"), 'w') as f:
        json.dump(license1, f)

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    test_org_map = result["testOrg"]

    # Canonical ID present
    assert "testorgid" in test_org_map
    assert test_org_map["testorgid"] == {"id": "testOrgId", "src": "testOrg"}

    # Alias present
    assert "testorg license" in test_org_map
    assert test_org_map["testorg license"] == {"id": "testOrgId", "src": "testOrg"}

    # Risky entries merged into org map
    assert "testorg-risky" in test_org_map
    assert test_org_map["testorg-risky"] == {"id": "testOrgId", "src": "testOrg"}


def test_read_org_data_multiple_orgs(tmpdir):
    orgs_dir = tmpdir.mkdir("orgs")
    test_org_dir = orgs_dir.mkdir("testOrg")
    acme_dir = orgs_dir.mkdir("acme")

    test_org_license = {
        "canonical": {"id": "testOrgId", "src": "testOrg"},
        "aliases": {"custom": ["testOrg License"]},
        "risky": []
    }
    acme_license = {
        "canonical": {"id": "ACME-1.0", "src": "acme"},
        "aliases": {"custom": ["ACME License"]},
        "risky": []
    }
    with open(test_org_dir.join("testOrgId.json"), 'w') as f:
        json.dump(test_org_license, f)
    with open(acme_dir.join("ACME-1.0.json"), 'w') as f:
        json.dump(acme_license, f)

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    assert "acme" in result


def test_read_org_data_no_orgs_dir(tmpdir):
    result = read_org_data(str(tmpdir))
    assert result == {}


def test_read_org_data_empty_org(tmpdir):
    tmpdir.mkdir("orgs").mkdir("testOrg")

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    assert result["testOrg"] == {}


def test_main_integration_with_orgs(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create main license files
        main_license = {
            "canonical": {"id": "MIT", "src": "spdx"},
            "aliases": {"source1": ["MIT License"]},
            "risky": ["mit-risky"]
        }
        with open(os.path.join(temp_dir, "MIT.json"), 'w') as f:
            json.dump(main_license, f)

        # Create org subdir with org license files
        org_dir = os.path.join(temp_dir, "orgs", "testOrg")
        os.makedirs(org_dir)
        org_license = {
            "canonical": {"id": "testOrgId", "src": "testOrg"},
            "aliases": {"custom": ["testOrg License"]},
            "risky": ["testOrg-risky"]
        }
        with open(os.path.join(org_dir, "testOrgId.json"), 'w') as f:
            json.dump(org_license, f)

        # Create temp output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_out:
            output_path = tmp_out.name

        try:
            monkeypatch.setattr('src.load.merge_data.DATA_DIR', temp_dir)
            monkeypatch.setattr('sys.argv', ['merge_data', '--output', output_path])
            main()

            with open(output_path, 'r') as f:
                output_data = json.load(f)

            assert "stableMap" in output_data
            assert "riskyMap" in output_data
            assert "testOrg" in output_data

            # Verify stableMap content
            assert "mit" in output_data["stableMap"]
            assert "mit license" in output_data["stableMap"]

            # Verify riskyMap content
            assert "mit-risky" in output_data["riskyMap"]

            # Verify testOrg content (canonical + aliases + risky merged)
            assert "testorgid" in output_data["testOrg"]
            assert "testorg license" in output_data["testOrg"]
            assert "testorg-risky" in output_data["testOrg"]
        finally:
            os.remove(output_path)


def test_merge_deduplicates_keys_without_changing_canonical_values(tmp_path):
    canonical = {"id": "MiXeD-1.0", "src": "TestSource"}
    license_data = {
        "canonical": canonical,
        "aliases": {"custom": ["MIXED LICENSE", "mixed license", "  Mixed License  "], "spdx": ["MiXeD-1.0"]},
        "risky": ["MIXED RISKY", "mixed risky"],
    }
    (tmp_path / "MiXeD-1.0.json").write_text(json.dumps(license_data), encoding="utf-8")

    result = read_data(str(tmp_path))
    assert result == {
        "stableMap": {"mixed-1.0": canonical, "mixed license": canonical},
        "riskyMap": {"mixed risky": canonical},
    }
    assert json.loads((tmp_path / "MiXeD-1.0.json").read_text("utf-8")) == license_data


@pytest.mark.parametrize("first, second", [
    ("Expat", "expat"), ("LICENÇA", "licença"), ("İ", "i\u0307"), ("ΟΣ", "ος"),
    ("‘Example’", "'example'"), ("  Example  ", "example"),
])
def test_merge_rejects_ambiguous_normalized_aliases(tmp_path, first, second):
    for canonical_id, alias in [("License-A", first), ("License-B", second)]:
        data = {"canonical": {"id": canonical_id, "src": "spdx"}, "aliases": {"custom": [alias]}}
        (tmp_path / f"{canonical_id}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="Conflicting stable mapping") as exc:
        read_data(str(tmp_path))
    assert repr(normalize_license_name(first)) in str(exc.value)
    assert "License-A" in str(exc.value)
    assert "License-B.json" in str(exc.value)


def test_merge_rejects_canonical_alias_collision(tmp_path):
    for filename, data in {
        "MIT.json": {"canonical": {"id": "MIT", "src": "spdx"}, "aliases": {}},
        "Other.json": {"canonical": {"id": "Other", "src": "custom"}, "aliases": {"custom": ["mIt"]}},
    }.items():
        (tmp_path / filename).write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Conflicting stable mapping"):
        read_data(str(tmp_path))


def test_merge_rejects_same_id_with_different_sources(tmp_path):
    for source in ["spdx", "custom"]:
        data = {"canonical": {"id": "MIT", "src": source}, "aliases": {}}
        (tmp_path / f"{source}.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Conflicting stable mapping"):
        read_data(str(tmp_path))


def test_merge_rejects_risky_collision_without_overwriting_output(tmp_path):
    source_dir = tmp_path / "data"
    source_dir.mkdir()
    for canonical_id, alias in [("License-A", "Ambiguous"), ("License-B", "AMBIGUOUS")]:
        data = {"canonical": {"id": canonical_id, "src": "spdx"}, "aliases": {}, "risky": [alias]}
        (source_dir / f"{canonical_id}.json").write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "mapping.json"
    output.write_text("existing output", encoding="utf-8")
    with pytest.raises(ValueError, match="Conflicting risky mapping"):
        merge_data_to_paths(str(source_dir), str(output))
    assert output.read_text("utf-8") == "existing output"


def test_merge_keeps_stable_and_risky_scopes_separate(tmp_path):
    stable = {"id": "License-A", "src": "spdx"}
    risky = {"id": "License-B", "src": "spdx"}
    (tmp_path / "License-A.json").write_text(json.dumps({"canonical": stable, "aliases": {"custom": ["Shared"]}}))
    (tmp_path / "License-B.json").write_text(json.dumps({"canonical": risky, "aliases": {}, "risky": ["SHARED"]}))
    result = read_data(str(tmp_path))
    assert result["stableMap"]["shared"] == stable
    assert result["riskyMap"]["shared"] == risky


def test_merge_rejects_org_stable_risky_collision(tmp_path):
    org_dir = tmp_path / "orgs" / "acme"
    org_dir.mkdir(parents=True)
    for canonical_id, field in [("Org-A", "aliases"), ("Org-B", "risky")]:
        data = {"canonical": {"id": canonical_id, "src": "acme"}, "aliases": {}}
        data[field] = {"custom": ["Shared"]} if field == "aliases" else ["SHARED"]
        (org_dir / f"{canonical_id}.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Conflicting organization 'acme' mapping"):
        read_org_data(str(tmp_path))


def test_merge_deduplicates_org_stable_risky_keys(tmp_path):
    org_dir = tmp_path / "orgs" / "acme"
    org_dir.mkdir(parents=True)
    canonical = {"id": "Org-A", "src": "acme"}
    data = {"canonical": canonical, "aliases": {"custom": ["Shared"]}, "risky": ["SHARED"]}
    (org_dir / "Org-A.json").write_text(json.dumps(data), encoding="utf-8")
    assert read_org_data(str(tmp_path)) == {"acme": {"org-a": canonical, "shared": canonical}}


def test_merge_keeps_organizations_separate(tmp_path):
    for org in ["acme", "other"]:
        org_dir = tmp_path / "orgs" / org
        org_dir.mkdir(parents=True)
        data = {"canonical": {"id": "Shared", "src": org}, "aliases": {"custom": ["SHARED"]}}
        (org_dir / "Shared.json").write_text(json.dumps(data), encoding="utf-8")
    assert read_org_data(str(tmp_path)) == {
        org: {"shared": {"id": "Shared", "src": org}} for org in ["acme", "other"]
    }


@pytest.mark.parametrize("field", ["canonical", "alias", "risky"])
@pytest.mark.parametrize("identifier", ["", " \t\n ", "\u00a0"])
def test_merge_rejects_empty_normalized_keys_without_overwriting_output(tmp_path, field, identifier):
    source_dir = tmp_path / "data"
    source_dir.mkdir()
    data = {
        "canonical": {"id": "Example-License", "src": "custom"},
        "aliases": {"custom": ["Allowed Name"]},
        "risky": [],
    }
    if field == "canonical":
        data["canonical"]["id"] = identifier
    elif field == "alias":
        data["aliases"]["custom"] = [identifier]
    else:
        data["risky"] = [identifier]
    (source_dir / "Example-License.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    output = tmp_path / "mapping.json"
    output.write_text("existing output", encoding="utf-8")
    with pytest.raises(ValueError, match="Empty normalized lookup key"):
        merge_data_to_paths(str(source_dir), str(output))
    assert output.read_text("utf-8") == "existing output"


def test_merge_rejects_blank_organization_lookup_key(tmp_path):
    org_dir = tmp_path / "orgs" / "acme"
    org_dir.mkdir(parents=True)
    data = {"canonical": {"id": "Org-License", "src": "acme"}, "aliases": {"custom": [" \t\n "]}}
    (org_dir / "Org-License.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Empty normalized lookup key"):
        read_org_data(str(tmp_path))


if __name__ == '__main__':
    pytest.main()

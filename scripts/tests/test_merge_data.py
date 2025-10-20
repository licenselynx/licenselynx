#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import os
import tempfile

import pytest
from src.load.merge_data import read_data, write_data, main


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
            "MIT": {
                "id": "MIT",
                "src": "spdx"
            },
            "MIT License": {
                "id": "MIT",
                "src": "spdx"
            },
            "MIT Open Source License": {
                "id": "MIT",
                "src": "spdx"
            },
            "GNU General Public License": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPL v3": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPLv3": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPL": {
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


if __name__ == '__main__':
    pytest.main()

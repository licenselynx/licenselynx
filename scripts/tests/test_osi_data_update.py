#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.update.OsiDataUpdate import OsiDataUpdate


def test_process_unrecognized_license_id_recognized():
    aliases = ["The MIT License", "MIT License"]
    data = {
        "canonical": {"id": "mit"},
        "aliases": {"custom": [], "osi": [], "spdx": ["MIT License"]},
        "rejected": [],
        "risky": [],
    }
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))), mock.patch("json.dump"):
        updater = OsiDataUpdate()
        updater.update_license_file = MagicMock()
        result = updater.process_unrecognized_license_id(aliases, "mit", "")

    assert result is None


def test_process_unrecognized_license_id_still_unrecognized():
    updater = OsiDataUpdate()
    updater.get_file_for_unrecognized_id = MagicMock(return_value=None)

    result = updater.process_unrecognized_license_id(["The MIT License"], "mit", "")

    assert result == "mit"


def test_process_unrecognized_license_id_resolves_gpl_to_only():
    updater = OsiDataUpdate()
    updater.get_file_for_unrecognized_id = MagicMock(return_value="GPL-3.0-only.json")
    updater.update_license_file = MagicMock()

    result = updater.process_unrecognized_license_id(
        ["GNU General Public License version 3"], "GPL-3.0", "gpl-3-0"
    )

    assert result is None
    updater.update_license_file.assert_called_once()
    assert updater.update_license_file.call_args.args[0] == "GPL-3.0-only"


def test_update_license_file_skips_equivalent_scancode_alias(tmp_path):
    updater = OsiDataUpdate()
    updater._DATA_DIR = str(tmp_path)
    filepath = tmp_path / "Apache-2.0.json"
    filepath.write_text(json.dumps({
        "canonical": {"id": "Apache-2.0", "src": "spdx"},
        "aliases": {
            "spdx": ["Apache License 2.0"],
            "custom": [],
            "scancodeLicensedb": ["Apache 2.0"],
        },
        "rejected": [],
        "risky": [],
    }))

    updater.update_license_file("Apache-2.0", ["Apache Software License 2.0", "apache-2-0"])

    data = json.loads(filepath.read_text())
    assert data["aliases"]["osi"] == ["Apache Software License 2.0"]


@pytest.fixture
def osi_data_update():
    updater = OsiDataUpdate()
    updater._LOGGER = MagicMock()
    updater._DATA_DIR = "mock_data_dir"
    return updater


def test_process_licenses(osi_data_update):
    license_list = [
        {"id": "osi-license-1", "spdx_id": "license-1", "name": "Test License 1"},
        {"id": "license-2", "spdx_id": "", "name": "Test License 2"},
    ]
    osi_data_update.download_json_file = MagicMock()
    osi_data_update.load_json_file = MagicMock(return_value=license_list)
    osi_data_update.update_license_file = MagicMock()
    osi_data_update.process_unrecognized_license_id = MagicMock(return_value="license-2")
    osi_data_update.delete_file = MagicMock()

    with patch("os.listdir", return_value=["license-1.json"]), patch("builtins.open", mock_open()):
        osi_data_update.process_licenses()

    osi_data_update.download_json_file.assert_called_once_with(
        "https://opensource.org/api/license", "osi_license_list.json"
    )
    osi_data_update.update_license_file.assert_called_once_with(
        "license-1", ["Test License 1", "osi-license-1"]
    )
    osi_data_update._LOGGER.info.assert_called_once_with("Unprocessed licenses: 1\n['license-2']")


def test_process_licenses_matches_spdx_id_case_insensitively(osi_data_update):
    osi_data_update.download_json_file = MagicMock()
    osi_data_update.load_json_file = MagicMock(return_value=[{
        "id": "nokia",
        "spdx_id": "NOKIA",
        "name": "Nokia Open Source License Version 1.0a",
    }])
    osi_data_update.update_license_file = MagicMock()
    osi_data_update.delete_file = MagicMock()

    with patch("os.listdir", return_value=["Nokia.json"]):
        osi_data_update.process_licenses()

    osi_data_update.update_license_file.assert_called_once_with(
        "Nokia", ["Nokia Open Source License Version 1.0a", "nokia"]
    )

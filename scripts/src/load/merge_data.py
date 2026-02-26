#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import argparse
import json
import os
from typing import Optional, Any

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def _process_license_file(filepath: str, stable_map: dict[Any, Any], risky_map: Optional[dict[Any, Any]] = None):
    with open(filepath, 'r') as f:
        license_data = json.load(f)
        canonical_id = license_data["canonical"]["id"]
        canonical_object = license_data["canonical"]
        aliases = license_data.get("aliases", {})

        stable_map[canonical_id] = canonical_object
        for source in aliases:
            for alias in aliases[source]:
                stable_map[alias] = canonical_object

        if risky_map is not None:
            risky_aliases = license_data.get("risky", [])
            for element in risky_aliases:
                risky_map[element] = canonical_object


def read_data(data_dir: str) -> dict[str, Any]:
    stable_map: dict[str, Any] = {}
    risky_map: dict[str, Any] = {}

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)

        if os.path.isdir(filepath):
            continue

        _process_license_file(filepath, stable_map, risky_map)

    return {"stableMap": stable_map, "riskyMap": risky_map}


def read_extra_data(extra_dir: str) -> dict:
    extra_maps: dict[str, dict] = {}
    if not os.path.exists(extra_dir):
        return extra_maps

    for org in os.listdir(extra_dir):
        org_dir = os.path.join(extra_dir, org)
        if not os.path.isdir(org_dir):
            continue

        org_map: dict[str, Any] = {}
        for filename in os.listdir(org_dir):
            filepath = os.path.join(org_dir, filename)
            if not os.path.isfile(filepath):
                continue

            _process_license_file(filepath, org_map)

        extra_maps[f"{org}Map"] = org_map
    return extra_maps


def write_data(alias_mapping: dict, output_path: str):
    with open(output_path, 'w') as outfile:
        json.dump(alias_mapping, outfile, indent=4)


def merge_data_to_paths(data_dir: str, output_path: str):
    data = read_data(data_dir)
    extra_dir = os.path.join(data_dir, 'extra')
    extra_data = read_extra_data(extra_dir)
    data.update(extra_data)

    write_data(data, output_path)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', '-o', required=True, type=str, help='Path for export file')

    args = parser.parse_args(argv)

    output_path = args.output

    merge_data_to_paths(DATA_DIR, output_path)


if __name__ == '__main__':
    main()

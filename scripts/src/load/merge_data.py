#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import argparse
import json
import os

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def read_data(data_dir: str) -> dict:
    canonical_dict = {}
    risky_dict = {}

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)

        if os.path.isdir(filepath):
            continue

        with open(filepath, 'r') as f:
            license_data = json.load(f)
            canonical_id = license_data["canonical"]["id"]
            canonical_object = license_data["canonical"]
            aliases = license_data.get("aliases", [])

            canonical_dict[canonical_id] = canonical_object
            for source in aliases:
                for alias in aliases[source]:
                    canonical_dict[alias] = canonical_object

            risky_aliases = license_data.get("risky")
            if not risky_aliases:
                continue
            for element in risky_aliases:
                risky_dict[element] = canonical_object
    data = {"stableMap": canonical_dict, "riskyMap": risky_dict}

    return data


def read_extra_data(extra_dir: str) -> dict:
    extra_maps = {}
    if not os.path.exists(extra_dir):
        return extra_maps

    for org in os.listdir(extra_dir):
        org_dir = os.path.join(extra_dir, org)
        if not os.path.isdir(org_dir):
            continue

        org_map = {}
        for filename in os.listdir(org_dir):
            filepath = os.path.join(org_dir, filename)
            if not os.path.isfile(filepath):
                continue

            with open(filepath, 'r') as f:
                license_data = json.load(f)
                canonical_object = license_data["canonical"]
                canonical_id = canonical_object["id"]
                aliases = license_data.get("aliases", [])

                org_map[canonical_id] = canonical_object
                for source in aliases:
                    for alias in aliases[source]:
                        org_map[alias] = canonical_object

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

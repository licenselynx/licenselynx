#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import argparse
import json
import os

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))

QUOTE_TRANSLATION = str.maketrans({
    quote: "'" for quote in "\u2018\u2019\u201a\u201b\u2032\uff07\u201c\u201d\u201e\u201f\u2033\u00ab\u00bb\uff02"
})


def normalize_license_name(license_name: str) -> str:
    """Normalize lookup keys using quotes, trimming, and Unicode lowercase."""
    return license_name.translate(QUOTE_TRANSLATION).strip().lower()


def _add_mapping(mapping: dict, identifier: str, canonical: dict, scope: str, filepath: str):
    key = normalize_license_name(identifier)
    if not key:
        raise ValueError(f"Empty normalized lookup key for {scope} mapping in {filepath!r}: {identifier!r}")
    existing = mapping.get(key)
    if existing is not None and existing != canonical:
        raise ValueError(
            f"Conflicting {scope} mapping for normalized key {key!r} in {filepath!r}: "
            f"{existing!r} and {canonical!r}"
        )
    mapping.setdefault(key, canonical)


def _build_maps_from_dir(data_dir: str) -> tuple[dict, dict]:
    """
    Reads all JSON files in data_dir and returns two dicts:
      - canonical_dict: normalized canonical IDs + all aliases -> canonical object
      - risky_dict: normalized risky entries -> canonical object

    Deduplicates keys with the same target and rejects conflicting targets within
    each map. Canonical objects keep their original casing.
    Skips non-JSON files and subdirectories.
    """
    canonical_dict: dict[str, dict] = {}
    risky_dict: dict[str, dict] = {}

    for filename in sorted(os.listdir(data_dir)):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            license_data = json.load(f)
            canonical_id = license_data["canonical"]["id"]
            canonical_object = license_data["canonical"]
            aliases = license_data.get("aliases", [])

            _add_mapping(canonical_dict, canonical_id, canonical_object, "stable", filepath)
            for source in aliases:
                for alias in aliases[source]:
                    _add_mapping(canonical_dict, alias, canonical_object, "stable", filepath)

            risky_aliases = license_data.get("risky")
            if not risky_aliases:
                continue
            for element in risky_aliases:
                _add_mapping(risky_dict, element, canonical_object, "risky", filepath)

    return canonical_dict, risky_dict


def read_data(data_dir: str) -> dict:
    canonical_dict, risky_dict = _build_maps_from_dir(data_dir)
    data = {"stableMap": canonical_dict, "riskyMap": risky_dict}
    return data


def read_org_data(data_dir: str) -> dict:
    """
    Auto-discovers org subdirectories under data_dir/orgs/ and builds
    one map per org.

    Returns:
        dict with keys matching org directory names (e.g. 'siemens'), each mapping
        normalized canonical IDs + aliases + risky entries -> canonical object.
        Returns empty dict if orgs/ does not exist.
    """
    orgs_path = os.path.join(data_dir, 'orgs')
    if not os.path.isdir(orgs_path):
        return {}

    org_maps: dict = {}
    for org_name in sorted(os.listdir(orgs_path)):
        org_dir_path = os.path.join(orgs_path, org_name)
        if not os.path.isdir(org_dir_path):
            continue
        canonical_dict, risky_dict = _build_maps_from_dir(org_dir_path)
        for key, canonical in risky_dict.items():
            _add_mapping(canonical_dict, key, canonical, f"organization '{org_name}'", org_dir_path)
        org_maps[org_name] = canonical_dict

    return org_maps


def write_data(alias_mapping: dict, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(alias_mapping, outfile, separators=(',', ':'))


def merge_data_to_paths(data_dir: str, output_path: str):
    data = read_data(data_dir)
    org_data = read_org_data(data_dir)
    data.update(org_data)

    write_data(data, output_path)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', '-o', required=True, type=str, help='Path for export file')

    args = parser.parse_args(argv)

    output_path = args.output

    merge_data_to_paths(DATA_DIR, output_path)


if __name__ == '__main__':
    main()

#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import logging
import json
import os
import re
from src.update.BaseDataUpdate import BaseDataUpdate
from src.update.canonical_source import CanonicalSource


class OsiDataUpdate(BaseDataUpdate):
    def __init__(self, src: CanonicalSource = CanonicalSource.OSI, debug=False):
        if debug:
            super().__init__(src=src, log_level=logging.DEBUG)
        else:
            super().__init__(src=src, log_level=logging.INFO)

    def update_license_file(self, canonical_id: str, aliases: list[str], alias_key: str | None = None) -> None:
        filepath = os.path.join(self._DATA_DIR, f"{canonical_id}.json")
        data = self.load_json_file(filepath)
        aliases_by_source = data.get("aliases", {})
        existing_aliases = [data["canonical"]["id"]]
        for source_aliases in aliases_by_source.values():
            existing_aliases.extend(source_aliases)

        existing_keys = {self._alias_key(alias) for alias in existing_aliases}
        risky_keys = {self._alias_key(alias) for alias in data.get("risky", [])}
        rejected_keys = {self._alias_key(alias) for alias in data.get("rejected", [])}
        new_aliases = [
            alias for alias in self._normalize_alias_list(aliases)
            if self._alias_key(alias) not in existing_keys | risky_keys | rejected_keys
        ]
        if not new_aliases:
            return

        source = alias_key or self._src
        aliases_by_source.setdefault(source, []).extend(new_aliases)
        aliases_by_source[source].sort(key=str.lower)

        with open(filepath, 'rb') as infile:
            infile.seek(-1, os.SEEK_END)
            had_trailing_newline = infile.read(1) == b'\n'
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)
            if had_trailing_newline:
                outfile.write('\n')

    @staticmethod
    def _alias_key(alias: str) -> str:
        return re.sub(r"[^\w]", "", alias.casefold())

    def process_unrecognized_license_id(self, aliases: list[str], license_id: str, osi_id: str) -> str | None:
        """
        Process unrecognized license to either find the license file with all the  license name variations or return the
        unprocessed license if no match is found

        Args:
            aliases: A list of aliases associated with this license
            license_id: id of the license
            osi_id: OSI identifier of the license

        Returns:
            unprocessed_license_id (string): id of the still unrecognized license or None if the license was found
        """

        # Get all variations of license and merge them into a list
        license_name_variations = []
        license_name_variations.extend(aliases)
        license_name_variations.extend({osi_id, license_id})

        filename = self.get_file_for_unrecognized_id(license_name_variations)

        unprocessed_license = None
        if not filename:
            self._LOGGER.warning(f"File not found for {license_id}. "
                                 f"Please verify manually the existence of the license file and either add the new "
                                 f"OSI license information or create a new license file in {self._DATA_DIR}")
            unprocessed_license = license_id
        else:
            license_id = filename.rsplit(".", 1)[0]

            self.update_license_file(license_id, license_name_variations)

        return unprocessed_license

    def process_licenses(self):
        """
        Processes the license list and updates the license entries
        """
        filepath = "osi_license_list.json"

        # Download and load the OSI license list
        self.download_json_file("https://opensource.org/api/license", filepath)
        license_list = self.load_json_file(filepath)

        files_by_id = {
            filename[:-5].casefold(): filename[:-5]
            for filename in os.listdir(self._DATA_DIR)
            if filename.endswith(".json")
        }
        unprocessed_licenses = []
        for entry in license_list:
            osi_id = entry["id"]
            license_id = entry["spdx_id"] or osi_id
            aliases = [entry["name"]]
            license_file_id = files_by_id.get(license_id.casefold())
            osi_file_id = files_by_id.get(osi_id.casefold())

            # Process licenses where both ids are unrecognized in an extra step
            if not (license_file_id or osi_file_id):
                unprocessed_license = self.process_unrecognized_license_id(aliases, license_id, osi_id)
                if unprocessed_license:
                    unprocessed_licenses.append(unprocessed_license)
            else:
                if license_file_id:
                    aliases.append(osi_id)
                    self.update_license_file(license_file_id, aliases)
                else:
                    aliases.append(license_id)
                    self.update_license_file(osi_file_id, aliases)
        if unprocessed_licenses:
            self._LOGGER.info(f"Unprocessed licenses: {len(unprocessed_licenses)}\n"
                              f"{unprocessed_licenses}")
        self.delete_file(filepath)

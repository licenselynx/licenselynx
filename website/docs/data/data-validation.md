# Data Validation

Before data is merged, LicenseLynx validates both the OSS license files and the organization-specific license files.

## Core Checks

These checks apply to every license file:

1. Filename must match `canonical.id`.
2. Canonical IDs and aliases must be unique across license files after quote normalization, trimming, and Unicode lowercasing.
3. `canonical.src` must be valid.
4. If `canonical.src` is `spdx`, `canonical.id` must exist in the SPDX license or exception lists.
5. `aliases` must only use these keys: `spdx`, `scancodeLicensedb`, `pypi`, `osi`, `custom`.
6. `canonical.id`, aliases, and `canonical.src` must not exceed 100 characters.
7. `canonical.id` must not contain `# $ % = [ ] ? < > : / \ | *` or spaces.
8. `canonical.id` must not be empty.
9. `aliases` must not be empty.
10. Alias lists must not be empty, except for `custom`.
11. `canonical.src` must not be empty.
12. The `rejected` field must exist.
13. An entry must not appear in both `aliases` and `rejected` after quote normalization, trimming, and Unicode lowercasing.
14. Alias versions must match the canonical version where version matching applies.
15. `isMajorVersionOnly` must match the canonical versioning pattern.
16. Risky aliases must also be unique after normalization, checked separately from the stable map.
17. Canonical identifiers, aliases, and risky entries must not normalize to an empty lookup key.

Case variants belonging to the same canonical license are allowed and deduplicated during merging.
Different targets in the same normalized map are rejected rather than overwritten. Stable and risky maps remain
separate; when both contain a key, the stable mapping takes precedence.

## Organization Checks

These checks apply to data under `data/orgs/`:

1. Organization folder names must be unique.
2. Organization folder names must not use reserved names like `stableMap` or `riskyMap`.
3. Every file inside an organization folder must use that organization name as `canonical.src`.
4. No normalized canonical identifier, alias, or risky entry may overlap between OSS data and organization data.
5. Organization aliases and risky entries share one organization map, so collisions between them are also checked.

Different organizations remain isolated and may use the same normalized lookup keys.

## Why This Exists

These checks catch structural problems early. They do not guarantee semantic correctness, which is why rejected entries and risky mappings still exist.

## Related Pages

- [Data Specification](data-specification.md)
- [Adding Mappings](../contributing/adding-mappings.md)
- [Organization Mappings](../contributing/organization-mappings.md)

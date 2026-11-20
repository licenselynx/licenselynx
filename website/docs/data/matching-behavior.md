# Matching Behavior

This page describes what happens to a license string before and during lookup.

Matching is case-insensitive by default: `Expat`, `expat`, and `eXpAt` all return canonical ID `MIT`.
Canonical identifiers and sources retain their original casing; risky and organization lookups remain opt-in.

## Unicode Lowercase

Inputs and merged lookup keys use locale-independent full Unicode lowercase:

| Implementation | Lowercase operation |
|----------------|---------------------|
| Data merger / Python | `str.lower()` |
| Java | `String.toLowerCase(Locale.ROOT)` |
| TypeScript | `String.toLowerCase()` |
| Go | `cases.Lower(language.Und).String(...)` from `golang.org/x/text` |

This includes expansions (`İ` becomes `i` + combining dot above) and contextual casing (`ΟΣ` becomes `ος`).
Go's standard `strings.ToLower` does not handle those rules, so Go uses the maintained text package instead.
Lowercase is not case folding: `ß` does not become `ss`. No accent removal, NFC/NFKC normalization, or internal whitespace collapsing is added.

Shared tests in `fixtures/normalization.json` cover Unicode rules and dataset lookups. Unicode table versions
can still differ across supported runtimes, particularly Java 8; identical behavior for every Unicode version is not guaranteed.

## Quote Normalization

Before lookup, LicenseLynx normalizes recognized Unicode quote characters to the ASCII single quote `'`.

This helps when license strings are copied from PDFs, websites, office documents, or other sources that use typographic quotes.

Examples:

- `BSD ‚Zero‛ Clause` becomes `BSD 'Zero' Clause`
- `Licensed under the “MIT” license` becomes `Licensed under the 'MIT' license`

## Lookup Order

Lookup happens in this order:

1. Normalize quote characters.
2. Trim surrounding whitespace.
3. Apply locale-independent Unicode lowercase.
4. Search the stable map.
5. If no match was found and `risky` is enabled, search the risky map.
6. If no match was found and `org` is provided, search that organization's map.

See [Risky Mappings](risky-mappings.md) for the meaning of the risky map.

Stable matches always take precedence. Both casing variants of `Nokia Qt LGPL exception 1.1` now resolve
to the stable `Nokia-Qt-exception-1.1` SPDX entry, even when risky mappings are enabled.

## Generated Data and Compatibility

Merged lookup keys are normalized and deduplicated within each map; conflicting targets cause merging to fail.
Source files, canonical values, and top-level names such as `stableMap` remain unchanged.
Direct JSON consumers must normalize input too. Code and mapping data must be updated together;
older clients expecting original-case keys must use a compatible versioned dataset or be updated.

## Recognized Quote Characters

All four libraries and the data merger normalize the same set of characters:

```python
quote_characters = [
    # Single quotes
    "\u2018",  # LEFT SINGLE QUOTATION MARK '
    "\u2019",  # RIGHT SINGLE QUOTATION MARK '
    "\u201A",  # SINGLE LOW-9 QUOTATION MARK ‚
    "\u201B",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK ‛
    "\u2032",  # PRIME (often used as an apostrophe) ′
    "\uFF07",  # FULLWIDTH APOSTROPHE ＇
    # Double quotes
    "\u201C",  # LEFT DOUBLE QUOTATION MARK "
    "\u201D",  # RIGHT DOUBLE QUOTATION MARK "
    "\u201E",  # DOUBLE LOW-9 QUOTATION MARK „
    "\u201F",  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK ‟
    "\u2033",  # DOUBLE PRIME ″
    "\u00AB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK «
    "\u00BB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK »
    "\uFF02",  # FULLWIDTH QUOTATION MARK ＂
]
```

## Related Pages

- [Usage](../usage.md)
- [API Reference](../api-reference.md)
- [Risky Mappings](risky-mappings.md)

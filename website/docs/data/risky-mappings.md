# Risky Mappings

## The Problem

Some license strings omit important version or later-version information. Returning a plausible mapping for
such a string would be a guess, which violates LicenseLynx's [data quality](data-quality.md) principle of deterministic mappings.
For a concrete dataset example, `Libpng License v2` is stored only in the risky map.

## How LicenseLynx Handles This

Instead of discarding ambiguous mappings entirely, LicenseLynx separates them into two tiers:

- **Stable map** (default) -- Only high-confidence, unambiguous mappings. This is what you get when you call `map()` without extra parameters.
- **Risky map** (opt-in) -- Plausible but uncertain mappings. Only searched when you explicitly enable it.

This way, the default behavior is always safe, but callers who prefer broader coverage over strict accuracy can opt in.
For the full lookup order, see [Matching Behavior](matching-behavior.md).
Both maps use case-insensitive matching. Lowercasing an input does not enable risky mappings, and a stable
match always takes precedence when both maps contain the same normalized key.

## When a Mapping Becomes Risky

A mapping is placed in the `risky` list of a license file when:

- The alias is ambiguous (could refer to multiple licenses)
- The alias lacks a version number where one is expected
- The mapping is based on common usage rather than an authoritative source
- The relationship between the alias and the canonical license is not fully verified

For family-specific conventions (for example the GNU `-only` risky default), see [Alias Decisions](alias-decisions.md).


## How to Enable

=== "Python"

    ```python
    from licenselynx.licenselynx import LicenseLynx

    # Stable only (default)
    result = LicenseLynx.map("LIBPNG LICENSE V2")  # None

    # With risky mappings
    result = LicenseLynx.map("LIBPNG LICENSE V2", risky=True)  # LicenseObject(id="libpng-2.0", src="spdx")
    ```

=== "Java"

    ```java
    import org.licenselynx.LicenseLynx;

    // Stable only (default)
    LicenseLynx.map("LIBPNG LICENSE V2");        // null

    // With risky mappings
    LicenseLynx.map("LIBPNG LICENSE V2", true);  // LicenseObject
    ```

=== "TypeScript"

    ```typescript
    import {map} from "@licenselynx/licenselynx";

    // Stable only (default)
    map('LIBPNG LICENSE V2');        // throws an error

    // With risky mappings
    map('LIBPNG LICENSE V2', true);  // returns libpng-2.0
    ```

## Relationship to Rejected Mappings

Rejected mappings are different from risky ones. A **rejected** alias is one that was explicitly marked as *wrong* for a license -- it will never be returned, regardless of the `risky` flag. Risky mappings are *plausible but uncertain*; rejected mappings are *known to be incorrect*.

See the [Data Specification](data-specification.md) for the full field definitions.

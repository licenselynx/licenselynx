# Alias Decisions

This page keeps track of alias decisions we did for LicenseLynx when we discovered ambiguity.

## GNU Licenses: `-only` as the Risky Default (Issues [#75](https://github.com/licenselynx/licenselynx/issues/75), [#86](https://github.com/licenselynx/licenselynx/issues/86))

Ambiguous GNU license aliases that don't encode `-only` or `-or-later` are mapped to the `-only` variant on
the [risky map](risky-mappings.md).

### Rule

For aliases like `gpl-2.0`, `GPLv2`, `GPL v2`, `GNU General Public License v2`, we place them into the `-only` files but in the risky list.

If an automated source maps suffixless aliases to `-or-later`, we keep those aliases out of the `-or-later` files so future auto-updates do not reintroduce them there.

Exceptions kept on the **stable** map as exact matches:

| Alias (exact) | Resolves to        | Reason                                                  |
|---------------|--------------------|---------------------------------------------------------|
| `GPL-2.0`     | `GPL-2.0-only`     | Deprecated SPDX ID, explicitly `-only` per SPDX history |
| `GPL-2.0+`    | `GPL-2.0-or-later` | Deprecated SPDX ID, explicitly `-or-later`              |

The same pattern applies to every `<family>-<version>` / `<family>-<version>+` deprecated SPDX ID.

### Reasoning

The FSF's guidance on identifying GNU
licenses ([gnu.org/licenses/identify-licenses-clearly](https://www.gnu.org/licenses/identify-licenses-clearly.html)) recommends making the
chosen variant explicit. Bare version references remain ambiguous because the actual license can depend on the license file, source headers,
or REUSE/SPDX tags that LicenseLynx does not inspect.

We also contacted Richard Stallman and asked him for his opinion, and his answer was the following quote:

>  **Richard Stallman's answer**
> 
> I suggest you urge them to make it unambiguous.

After further discussion in [#83](https://github.com/licenselynx/licenselynx/discussions/83), we changed the risky default from `-or-later` to `-only`.
If `GPL 2.0` was intended as `GPL-2.0-or-later`, mapping it to `GPL-2.0-only` omits a permitted later-version option.
If it was intended as `GPL-2.0-only`, mapping it to `GPL-2.0-or-later` would add license options the licensor may not have granted.
The latter mistake has a higher impact, so ambiguous GNU versioned aliases resolve to `-only` only when callers opt into risky mappings.

### Scope

Applies to all GNU license families with `-only` / `-or-later` variants:

- GPL 1.0, 2.0, 3.0
- LGPL 2.0, 2.1, 3.0
- AGPL 1.0, 3.0
- GFDL 1.1, 1.2, 1.3

### PyPI Classifiers

PyPI trove classifiers like `License :: OSI Approved :: GNU General Public License v2 (GPLv2)` encode no `-only`/`-or-later` distinction and
are treated similar to the other aliases, i.e. mapped to `-only` on the risky map.

# LicenseLynx for Python

To use LicenseLynx in Python, you can call the ``map`` method from the ``LicenseLynx`` module to map a license name to its canonical form.
The return value is an object with the canonical name and the source of the license.

## Installation

Requires Python **3.9** or higher. Python 3.9 compatibility is retained for downstream integrations;
Python 3.9 reached upstream end-of-life in October 2025. Use a maintained Python version where possible.

To install the library, run following command:

```shell
pip install licenselynx 
```

## Usage

```python
from licenselynx.licenselynx import LicenseLynx

# Map the license name
license_object = LicenseLynx.map("licenseName")

print(license_object.id)
print(license_object.src)

# Map the license name with risky mappings enabled
license_object = LicenseLynx.map("licenseName", risky=True)

```

## Organization Licenses

Organizations can register internal/proprietary license identifiers that are kept separate from OSS licenses.
To look up an organization license, pass the `org` parameter:

```python
from licenselynx.licenselynx import LicenseLynx
from licenselynx import Organization

# Map a license name within an organization
license_object = LicenseLynx.map("licenseName", org=Organization.SIEMENS)
```

The `LicenseSource` enum is also available for inspecting the source type:

```python
from licenselynx import LicenseSource
```

Helper methods on the returned license object:

```python
# Check if the license comes from any organization
license_object.is_organization_source()  # returns True if from any org

# Check if the license comes from a specific organization
license_object.is_organization_source_of(Organization.SIEMENS)  # returns True if from Siemens
```

## Development and compatibility testing

Use Poetry **2.4.3** to install dependencies and maintain `poetry.lock`. CI tests Python 3.9–3.14, including smoke tests against the built wheel.
Linting and release tooling run on modern Python.

Pytest is a development dependency and is not installed with LicenseLynx. Python 3.9 uses pytest 8.4.2; newer Python versions use a patched pytest 9 release.
The legacy version is affected by [CVE-2025-71176](https://osv.dev/vulnerability/GHSA-6w46-j5rx-g56g) (Unix temporary-directory handling), with no upstream Python 3.9-compatible fix.
The Python 3.9 CI jobs use disposable GitHub-hosted runners and a private temporary directory. This mitigates exposure but does not remove the dependency advisory.
For local legacy testing, use an isolated environment and a private temporary root:

```shell
private_tmp=$(mktemp -d)
TMPDIR="$private_tmp" poetry run python -m pytest -m "not smoke"
```

Revisit Python 3.9 support when downstream integrations no longer require it.

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED

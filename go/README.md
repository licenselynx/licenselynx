# LicenseLynx for Go

In Go, you can call `Map` from the `licenselynx` package to map a license name to its canonical form.
The return value is a `LicenseObject` together with a boolean indicating whether a match was found.

## Installation

To install the library, run the following command:

```shell
go get github.com/licenselynx/licenselynx/go
```

## Usage

```go
package main

import (
	"fmt"

	"github.com/licenselynx/licenselynx/go"
)

func main() {
	licenseObject, ok := licenselynx.Map("MIT")
	if !ok {
		panic("license not found")
	}

	fmt.Println(licenseObject.ID)
	fmt.Println(licenseObject.Src)

	riskyLicenseObject, ok := licenselynx.Map("License :: LGPLv3", licenselynx.WithRisky())
	if ok {
		fmt.Println(riskyLicenseObject.ID)
	}
}
```

## Organization Licenses

Organizations can register internal or proprietary license identifiers that are kept separate from OSS licenses.
To look up an organization license, pass `WithOrganization`:

```go
licenseObject, ok := licenselynx.Map("SISL 1.5", licenselynx.WithOrganization(licenselynx.OrgSiemens))
```

Helper methods on the returned object:

```go
licenseObject.IsSpdxId()
licenseObject.IsScancodeLicenseId()
licenseObject.IsCustomId()
licenseObject.IsOrganizationSource()
licenseObject.IsOrganizationSourceOf(licenselynx.OrgSiemens)
```

## Development

Generated lookup tables are committed to git. To regenerate them locally:

```shell
mkdir -p _support
python3 scripts/src/load/merge_data.py -o _support/merged_data.build.json
cd go
go generate ./...
```

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED

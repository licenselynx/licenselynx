# Usage

The `map` method is the core of every LicenseLynx library. It takes a license name string and returns a `LicenseObject` containing the canonical `id` and its `src` (source).

For the full method signatures, parameters, and error handling, see the [API Reference](api-reference.md).

Matching normalizes quotes, trims whitespace, and applies locale-independent Unicode lowercase.
`Expat`, `expat`, and `eXpAt` all resolve to `MIT`, preserving canonical `id` and `src` casing.

If no match is found, Python returns `None`, Java returns `null`, and TypeScript rejects the `Promise`.
For Unicode details and lookup order, see [Matching Behavior](data/matching-behavior.md).

## Python

```python
from licenselynx.licenselynx import LicenseLynx

result = LicenseLynx.map("MIT")
print(result.id)   # "MIT"
print(result.src)  # "spdx"
```

## Java

```java
import org.licenselynx.LicenseLynx;
import org.licenselynx.LicenseObject;

LicenseObject result = LicenseLynx.map("MIT");
System.out.println(result.getId());   // "MIT"
System.out.println(result.getSrc());  // "spdx"
```

## TypeScript

`map` returns a `LicenseObject`.

```typescript
import { map } from "@licenselynx/licenselynx";

const result = map("MIT");
console.log(result.id); // "MIT"
console.log(result.src); // "spdx"
```

## Go

```go
package main

import (
	"fmt"

	"github.com/licenselynx/licenselynx/v2/go"
)

func main() {
	licenseObject, ok := licenselynx.Map("MIT")
	if !ok {
		panic("license not found")
	}

	fmt.Println(licenseObject.ID) // "MIT"
	fmt.Println(licenseObject.Src) // "spdx"
}
```

## Risky Mappings

All languages support an optional `risky` parameter. When enabled, the lookup falls back to lower-confidence mappings if no match is found in the stable map. See [Risky Mappings](data/risky-mappings.md) for details.

=== "Python"

    ```python
    result = LicenseLynx.map("LIBPNG LICENSE V2", risky=True)
    ```

=== "Java"

    ```java
    LicenseObject result = LicenseLynx.map("LIBPNG LICENSE V2", true);
    ```

=== "TypeScript"

    ```typescript
    const result = map('LIBPNG LICENSE V2', true);
    ```

=== "Go"

    ```go
    riskyLicenseObject, ok := licenselynx.Map("LIBPNG LICENSE V2", licenselynx.WithRisky())
	if ok {
		fmt.Println(riskyLicenseObject.ID)
	}
    ```

## Organization Mappings

All languages support an optional `org` parameter for looking up organization-specific licenses (e.g., inner-source licenses). See the [API Reference](api-reference.md#organization) for the full `Organization` enum.

=== "Python"

    ```python
    from licenselynx.organization import Organization

    result = LicenseLynx.map("SISL-1.4", org=Organization.SIEMENS)
    ```

=== "Java"

    ```java
    import org.licenselynx.Organization;

    LicenseObject result = LicenseLynx.map("SISL-1.4", Organization.Siemens);
    ```

=== "TypeScript"

    ```typescript
    import {map, Organization} from "@licenselynx/licenselynx";

    const result = map('SISL-1.4', false, Organization.Siemens);
    ```
=== "Go"

    ```go
    licenseObject, ok := licenselynx.Map("SISL 1.5", licenselynx.WithOrganization(licenselynx.OrgSiemens))
    ```

## Data Mapping

The full license mapping is also available as a JSON file at [`/json/latest/mapping.json`](https://licenselynx.org/json/latest/mapping.json).
Its lookup keys are normalized lowercase strings; direct JSON consumers must normalize input before indexing a map.
See the [Data Specification](data/data-specification.md) for the format.

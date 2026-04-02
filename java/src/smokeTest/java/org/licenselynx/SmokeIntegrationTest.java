/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;


/**
 * Smoke integration tests that run against the built jar with real merged data.
 */
@Tag("smoke")
class SmokeIntegrationTest
{
    @Test
    void stableMapLookup()
    {
        LicenseObject result = LicenseLynx.map("0BSD");
        assertNotNull(result, "Expected a result for '0BSD'");
        assertEquals("0BSD", result.getId());
        assertEquals(LicenseSource.Spdx, result.getCanonicalSource());
    }

    @Test
    void riskyMapLookupWithFlag()
    {
        LicenseObject result = LicenseLynx.map("LIbpng License v2", true);
        assertNotNull(result, "Expected a result for 'LIbpng License v2' with risky=true");
        assertEquals("libpng-2.0", result.getId());
    }

    @Test
    void riskyEntryNotResolvedWithoutFlag()
    {
        LicenseObject result = LicenseLynx.map("LIbpng License v2");
        assertNull(result, "Expected null for 'LIbpng License v2' without risky=true");
    }

    @Test
    void organizationScopedLookup()
    {
        LicenseObject result = LicenseLynx.map("Siemens Inner Source License v1.5", Organization.Siemens);
        assertNotNull(result, "Expected a result for Organization.Siemens");
        assertEquals("SISL-1.5", result.getId());
        assertEquals("siemens", result.getCanonicalSource().getValue());
    }

    @Test
    void organizationEntryNotResolvedWithoutOrg()
    {
        LicenseObject result = LicenseLynx.map("Siemens Inner Source License v1.5");
        assertNull(result, "Expected null without org parameter");
    }
}
